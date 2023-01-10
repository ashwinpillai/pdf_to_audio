import os
from flask import Flask, flash, request, redirect, url_for,render_template,send_from_directory
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
import pyttsx3
import uuid



app = Flask(__name__)

ALLOWED_EXTENSIONS = {'pdf'}
app.config['MAX_CONTENT_LENGTH'] = 5 * 1000 * 1000

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pdf_to_voice(file,sound):
    global audio_file
    reader = PdfReader(file)
    number_of_pages = len(reader.pages)
    text = ""
    for i in range(number_of_pages):
        page = reader.pages[i]
        text += page.extract_text() 

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[sound].id)
    audio_file = f'./static/audios/{uuid.uuid1()}.mp3'
    engine.save_to_file(text, audio_file)
    engine.runAndWait()



@app.route('/')
def home():
    return render_template("index.html")

@app.route('/convert',methods=['GET', 'POST'])
def convert():
    if request.method == 'POST':
        if 'pdf' not in request.files:
            flash("no file")
            return redirect(request.url)
        file = request.files['pdf']
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            sfilename = secure_filename(file.filename)
            pdf_path = os.path.join('./static/uploadedPDF', sfilename)
            file.save(pdf_path)
            print("file saved")
            #return redirect(url_for('uploaded_file', filename=filename))
        sound = int(request.form.get('chosen_voice'))
        pdf_to_voice(pdf_path,sound)

        
    
    return render_template("audio.html",audio_file=audio_file)

if __name__ == '__main__':
    app.run(debug=True)