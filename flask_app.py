import os
import io
import datetime
import uuid
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from gtts import gTTS
from threading import Timer

ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1000 * 1000

def get_database_connection():
    return sqlite3.connect('Account.db')

def create_table():
    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Signup(
            Signup_id TEXT PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            Email VARCHAR NOT NULL,
            password VARCHAR NOT NULL,   
            Cpassword VARCHAR NOT NULL  
                     
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS AudioFiles(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        audio_path TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Signup (Signup_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UploadedFiles(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        pdf_path TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Signup (Signup_id)
        )
    ''')

    conn.commit()

def save_audio_file(user_id, audio_file_path):
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO AudioFiles (user_id, audio_path, created_at) VALUES (?, ?, ?)",
                   (user_id, audio_file_path, datetime.datetime.now()))
    conn.commit()
    conn.close()

def save_uploaded_pdf(user_id, pdf_path):
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO UploadedFiles (user_id, pdf_path, created_at) VALUES (?, ?, ?)",
                   (user_id, pdf_path, datetime.datetime.now()))
    conn.commit()
    conn.close()

def get_user_audio_files(user_id):
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT audio_path, DATE(created_at) FROM AudioFiles WHERE user_id = ?", (user_id,))
    audio_files = cursor.fetchall()
    close_db_connection(conn)
    return audio_files


def close_db_connection(conn):
    if conn:
        conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pdf_to_voice(file, sound, user_id):
    global audio_file
    reader = PdfReader(file)
    number_of_pages = len(reader.pages)
    text = ""
    for i in range(number_of_pages):
        page = reader.pages[i]
        text += page.extract_text() 

    language = 'en-us' if sound == 'en-us' else 'hi'

    tts = gTTS(text=text, lang=language)
    audio_file_path = f'./static/audios/{uuid.uuid1()}.mp3'

    # Save the spoken text to an audio file
    tts.save(audio_file_path)

    # Save the audio file along with the user_id
    save_audio_file(user_id, audio_file_path)

    # Set the global audio_file variable (not sure if you really need this global variable)
    audio_file = audio_file_path


def schedule_folder_clean():
    # Schedule the folder cleaning task to run every 10 days
    duration = 10 * 24 * 60 * 60  # 10 days in seconds
    Timer(duration, schedule_folder_clean).start()
    clean_folder("./static/audios")

def clean_folder(folder_path):
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)

create_table()

def is_logged_in():
    return 'user_id' in session

def delete_audio_file(audio_file_path):
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM AudioFiles WHERE audio_path = ?", (audio_file_path,))
    conn.commit()
    close_db_connection(conn)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if not is_logged_in():
        return render_template('access_denied.html')
    else:
        return render_template("index.html", name=session['user_name'])

@app.route('/audio_files', methods=['GET', 'POST'])
def audio_files():
    if not is_logged_in():
        return render_template('access_denied.html')
    else:
        user_id = session['user_id']
        user_name = session['user_name']  

        if request.method == 'POST':
            audio_file_id = request.form.get('id')
            delete_audio_file(audio_file_id)
            # Redirect to the same page after deletion
            return redirect(url_for('audio_files'))

        audio_files = get_user_audio_files(user_id)
        return render_template("audio_files.html", audio_files=audio_files, user_name=user_name)

@app.route('/my_files')
def my_files():
    if not is_logged_in():
        return render_template('access_denied.html')
    else:
        user_id = session['user_id']
        user_name = session['user_name']

        # Fetch PDF files uploaded by the current user from the database
        user_pdf_files = get_user_pdf_files(user_id)

        return render_template("my_files.html", user_pdf_files=user_pdf_files, user_name=user_name)

def get_user_pdf_files(user_id):
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT pdf_path, DATE(created_at) FROM UploadedFiles WHERE user_id = ?", (user_id,))
    pdf_files = cursor.fetchall()
    close_db_connection(conn)
    # Extract only the filename from the full path
    pdf_files = [(os.path.basename(pdf_path), created_at) for pdf_path, created_at in pdf_files]
    return pdf_files


# @app.route('/download/<path:filename>', methods=['GET'])
# def download(filename):
#     # Check if the user is logged in
#     if not is_logged_in():
#         return render_template('access_denied.html')

#     # Ensure that the file requested for download belongs to the logged-in user
#     user_id = session['user_id']
#     conn = get_database_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM AudioFiles WHERE id = ? AND user_id = ?", (filename, user_id))
#     audio_file = cursor.fetchone()
#     close_db_connection(conn)

#     if audio_file:
#         # Fetch the path of the audio file
#         audio_file_path = audio_file[2]

#         # Extract the filename from the path
#         filename = os.path.basename(audio_file_path)

#         # Send the file for download
#         return send_from_directory(directory='./static/audios', filename=filename, as_attachment=True)
#     else:
#         # If the requested file does not belong to the logged-in user, return access denied page
#         return render_template('access_denied.html')

def validate_login(email, password):
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Signup WHERE Email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    cursor.close()
    close_db_connection(conn)
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')  # Get the value of remember_me checkbox

        if not (email and password):
            return render_template("login.html", error_msg="Email and password are required.")

        user = validate_login(email, password)

        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]

            # Set a session cookie with a longer expiration time if "Remember Me" is checked
            if remember_me:
                session.permanent = True  # Make the session permanent
                app.permanent_session_lifetime = datetime.timedelta(days=30)  # Set expiration time (e.g., 30 days)

            return redirect(url_for('index'))
        else:
            return render_template("login.html", error_msg="Invalid email or password.")

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')

        if not (name and email and password and cpassword):
            return render_template("signup.html", error_msg="All fields are required.")

        if password != cpassword:
            return render_template("signup.html", error_msg="Passwords do not match.")

        signup_id = str(uuid.uuid4())

        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Signup (Signup_id, name, Email, password, Cpassword) VALUES (?, ?, ?, ?, ?)",
                       (signup_id, name, email, password, cpassword))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('login'))

@app.route('/delete_pdf', methods=['POST'])
def delete_pdf():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'User not logged in'})

    pdf_path = request.form.get('pdf_path')

    # Ensure that the PDF file belongs to the logged-in user
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'User ID not found in session'})

    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM UploadedFiles WHERE pdf_path = ? AND user_id = ?", (pdf_path, user_id))
        pdf_file = cursor.fetchone()

        if pdf_file:
            # Delete the PDF file from the database
            cursor.execute("DELETE FROM UploadedFiles WHERE pdf_path = ?", (pdf_path,))
            conn.commit()

            # Delete the PDF file from the file system
            os.remove(pdf_path)

            close_db_connection(conn)

            return jsonify({'success': True, 'message': 'PDF file deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'PDF file not found or does not belong to the user'})
    except sqlite3.Error as e:
        return jsonify({'success': False, 'message': 'Database error: ' + str(e)})
    except OSError as e:
        return jsonify({'success': False, 'message': 'File system error: ' + str(e)})
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred: ' + str(e)})

@app.route('/convert', methods=['POST'])
def convert():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'User not logged in'})

    if 'pdf' not in request.files:
        return jsonify({'success': False, 'message': 'No file chosen. Please upload a file'})

    file = request.files['pdf']

    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file chosen. Please upload a file'})

    if file and allowed_file(file.filename):
        sfilename = secure_filename(file.filename)
        pdf_path = os.path.join('static', 'uploadedPDF', sfilename)
        file.save(pdf_path)
        sound = request.form.get('chosen_voice')
        
        # Pass session['user_id'] to pdf_to_voice
        pdf_to_voice(pdf_path, sound, session['user_id'])

        save_uploaded_pdf(session['user_id'], pdf_path)


        # Notify the client that the conversion is complete
        return jsonify({'success': True, 'message': 'Congratulations! Audio Converted'})

    else:
        return jsonify({'success': False, 'message': 'Only pdf files are allowed'})
if __name__ == '__main__':
    app.run(debug=True)

    schedule_folder_clean()
