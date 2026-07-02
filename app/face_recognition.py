import numpy as np
import sklearn
import pickle
import cv2
import os

# Get directory path of the current file and determine absolute base directory
_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_DIR_PATH)

# Load all models
haar = cv2.CascadeClassifier(os.path.join(_BASE_DIR, 'model', 'haarcascade_frontalface_default.xml')) # cascade classifier
model_svm =  pickle.load(open(os.path.join(_BASE_DIR, 'model', 'model_svm.pickle'),mode='rb')) # machine learning model (SVM)
pca_models = pickle.load(open(os.path.join(_BASE_DIR, 'model', 'pca_dict.pickle'),mode='rb')) # pca dictionary
model_pca = pca_models['pca'] # PCA model
mean_face_arr = pca_models['mean_face'] # Mean Face

# Patch PCA compatibility across scikit-learn versions
if not hasattr(model_pca, 'power_iteration_normalizer'):
    model_pca.power_iteration_normalizer = 'auto'

# Load Caffe Age Model
age_net = cv2.dnn.readNetFromCaffe(
    os.path.join(_BASE_DIR, 'model', 'age_deploy.prototxt'),
    os.path.join(_BASE_DIR, 'model', 'age_net.caffemodel')
)
age_list = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)


def faceRecognitionPipeline(filename, path=True, analysis_mode='both', filter_gender='all'):
    if path:
        # step-01: read image
        img = cv2.imread(filename) # BGR
    else:
        img = filename # array
    # step-02: convert into gray scale
    gray =  cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) 
    # step-03: crop the face (using haar cascase classifier)
    faces = haar.detectMultiScale(gray, 1.3, 5)
    predictions = []
    for x,y,w,h in faces:
        #cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
        roi = gray[y:y+h,x:x+w]

        # step-04: normalization (0-1)
        roi = roi / 255.0
        # step-05: resize images (100,100)
        if roi.shape[1] > 100:
            roi_resize = cv2.resize(roi,(100,100),cv2.INTER_AREA)
        else:
            roi_resize = cv2.resize(roi,(100,100),cv2.INTER_CUBIC)

        # step-06: Flattening (1x10000)
        roi_reshape = roi_resize.reshape(1,10000)
        # step-07: subtract with mean
        roi_mean = roi_reshape - mean_face_arr # subtract face with mean face
        # step-08: get eigen image (apply roi_mean to pca)
        eigen_image = model_pca.transform(roi_mean)
        # step-09 Eigen Image for Visualization
        eig_img = model_pca.inverse_transform(eigen_image)
        
        # step-10: pass to ml model (svm) and get predictions if needed
        run_gender = (analysis_mode in ['gender', 'both']) or (filter_gender != 'all')
        if run_gender:
            results = model_svm.predict(eigen_image)
            prob_score = model_svm.predict_proba(eigen_image)
            prob_score_max = prob_score.max()
            gender_name = results[0]
        else:
            gender_name = 'unknown'
            prob_score_max = 0.0

        # Apply gender filter
        if filter_gender == 'male' and gender_name != 'male':
            continue
        if filter_gender == 'female' and gender_name != 'female':
            continue

        # Predict Age using Caffe model
        run_age = (analysis_mode in ['age', 'both'])
        if run_age:
            face_color = img[y:y+h, x:x+w]
            blob = cv2.dnn.blobFromImage(face_color, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
            age_net.setInput(blob)
            age_preds = age_net.forward()
            age_index = age_preds[0].argmax()
            predicted_age = age_list[age_index]
            age_score = age_preds[0][age_index]
        else:
            predicted_age = 'unknown'
            age_score = 0.0

        # step-11: generate report overlay text
        text_parts = []
        if analysis_mode in ['gender', 'both']:
            text_parts.append("%s: %d%%" % (gender_name.capitalize(), prob_score_max * 100))
        if analysis_mode in ['age', 'both']:
            text_parts.append("Age: %s" % predicted_age)
        text = " | ".join(text_parts)

        # defining color based on results
        if gender_name == 'male':
            color = (255, 255, 0)   # Cyan (BGR)
        elif gender_name == 'female':
            color = (255, 0, 255)   # Magenta (BGR)
        else:
            color = (255, 0, 128)   # Violet (BGR)

        # Dynamic overlay box rendering
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        
        # Calculate text width/height for label background
        (text_w, text_h), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(img, (x, y - text_h - 15), (x + max(w, text_w + 10), y), color, -1)
        cv2.putText(img, text, (x + 5, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

        output = {
            'roi': roi,
            'eig_img': eig_img,
            'prediction_name': gender_name,
            'score': prob_score_max,
            'age': predicted_age,
            'age_score': age_score
        }

        predictions.append(output)

    return img, predictions