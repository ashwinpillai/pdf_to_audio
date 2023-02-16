import os
from flask import Flask,request, render_template
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
#import pyttsx3
from gtts import gTTS
import uuid
from threading import Timer



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

     #engine = pyttsx3.init("dummy")
    #voices = engine.getProperty('voices')
    #engine.setProperty('voice', voices[sound].id)
    tts = gTTS(text=text, lang='en-us')
    audio_file = f'./static/audios/{uuid.uuid1()}.mp3'

    # Save the spoken text to an audio file
    tts.save(audio_file)
    #engine.save_to_file(text, audio_file)
    #engine.runAndWait()

def clean_folder(folder_path):
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)

def schedule_folder_clean():
    Timer(120, schedule_folder_clean).start() # schedule the next cleaning in 2 minutes
    clean_folder("./static/audios")

schedule_folder_clean()


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/convert',methods=['GET', 'POST'])
def convert():

    if request.method == 'POST':

        if 'pdf' not in request.files:
            error_msg="No file chosen. Please upload a file"
            return render_template("index.html",error_msg=error_msg)

        file = request.files['pdf']

        if file.filename == '':
            error_msg="No file chosen. Please upload a file"
            return render_template("index.html",error_msg=error_msg)

        if file and allowed_file(file.filename):
            sfilename = secure_filename(file.filename)
            pdf_path = os.path.join('./static/uploadedPDF', sfilename)
            file.save(pdf_path)
            sound = int(request.form.get('chosen_voice'))
            pdf_to_voice(pdf_path,sound)
            os.remove(pdf_path)

        else:
            error_msg="Only pdf files are allowed"
            return render_template("index.html",error_msg=error_msg)

    return render_template("audio.html",audio_file=audio_file)

if __name__ == '__main__':
    app.run(debug=True)