import os
import cv2
import time
from app.face_recognition import faceRecognitionPipeline
from flask import render_template, request
import matplotlib.image as matimg
import tempfile


# Dynamic detection of read-only filesystems (like Vercel)
UPLOAD_FOLDER = 'static/upload'
PREDICT_FOLDER = './static/predict'
IS_READ_ONLY = False

try:
    # Test writing to static/upload
    test_file_path = os.path.join(UPLOAD_FOLDER, '.write_test')
    with open(test_file_path, 'w') as test_file:
        test_file.write('test')
    os.remove(test_file_path)
except Exception:
    IS_READ_ONLY = True
    # Fallback to system's temp directory
    UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'face_app_upload')
    PREDICT_FOLDER = os.path.join(tempfile.gettempdir(), 'face_app_predict')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PREDICT_FOLDER, exist_ok=True)


def index():
    return render_template('index.html')


def app():
    return render_template('app.html')


def genderapp():
    if request.method == 'POST':
        f = request.files['image_name']
        filename = f.filename
        # retrieve options
        analysis_mode = request.form.get('analysis_mode', 'both')
        filter_gender = request.form.get('filter_gender', 'all')
        
        # save our image in upload folder
        path = os.path.join(UPLOAD_FOLDER,filename)
        f.save(path) # save image into upload folder
        # get predictions
        pred_image, predictions = faceRecognitionPipeline(path, analysis_mode=analysis_mode, filter_gender=filter_gender)
        pred_filename = 'prediction_image.jpg'
        cv2.imwrite(os.path.join(PREDICT_FOLDER, pred_filename),pred_image)
        
        # generate report
        report = []
        for i , obj in enumerate(predictions):
            gray_image = obj['roi'] # grayscale image (array)
            eigen_image = obj['eig_img'].reshape(100,100) # eigen image (array)
            gender_name = obj['prediction_name'] # name 
            score = round(obj['score']*100,2) # probability score
            age_name = obj['age']
            age_score = round(obj['age_score']*100,2)
            
            # save grayscale and eigne in predict folder
            gray_image_name = f'roi_{i}.jpg'
            eig_image_name = f'eigen_{i}.jpg'
            matimg.imsave(os.path.join(PREDICT_FOLDER, gray_image_name),gray_image,cmap='gray')
            matimg.imsave(os.path.join(PREDICT_FOLDER, eig_image_name),eigen_image,cmap='gray')
            
            # save report 
            report.append([gray_image_name,
                           eig_image_name,
                           gender_name,
                           score,
                           age_name,
                           age_score])
            
        
        return render_template('gender.html',
                               fileupload=True,
                               report=report,
                               timestamp=time.time(),
                               analysis_mode=analysis_mode,
                               filter_gender=filter_gender) # POST REQUEST
            
    
    
    return render_template('gender.html',
                           fileupload=False,
                           analysis_mode='both',
                           filter_gender='all') # GET REQUEST