from flask import Flask, send_from_directory
from app import views

app = Flask(__name__) # webserver gateway interphase (WSGI)

app.add_url_rule(rule='/',endpoint='home',view_func=views.index)
app.add_url_rule(rule='/app/',endpoint='app',view_func=views.app)
app.add_url_rule(rule='/app/gender/',
                 endpoint='gender',
                 view_func=views.genderapp,
                 methods=['GET','POST'])

# Transparently route /static/predict and /static/upload requests to the fallback temp folder if the filesystem is read-only.
@app.route('/static/predict/<path:filename>')
def custom_predict_static(filename):
    from app.views import IS_READ_ONLY, PREDICT_FOLDER
    if IS_READ_ONLY:
        return send_from_directory(PREDICT_FOLDER, filename)
    else:
        return send_from_directory('./static/predict', filename)

@app.route('/static/upload/<path:filename>')
def custom_upload_static(filename):
    from app.views import IS_READ_ONLY, UPLOAD_FOLDER
    if IS_READ_ONLY:
        return send_from_directory(UPLOAD_FOLDER, filename)
    else:
        return send_from_directory('./static/upload', filename)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)