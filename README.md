# Flask PDF to Audio Converter

This is a Flask web application that allows users to convert PDF files into audio files. Users can upload PDF files, choose the desired voice for the audio output, and then download the converted audio files.

# Step 1: Create a virtual environment (optional)
# Skip this step if you already have a virtual environment set up

# Create a virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate-- if error ocurss while activating
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted -Force

pip install -r requirements.txt


## Features

- User authentication: Users can sign up, log in, and log out.
- PDF upload: Users can upload PDF files to the server.
- Audio conversion: PDF files are converted to audio files using text-to-speech (TTS) technology.
- Voice selection: Users can choose between different voices for the audio output.
- Download audio: Users can download the converted audio files.
- Audio file management: Users can view and delete their uploaded audio files.

## Requirements

To run this application, you need the following dependencies installed:

- Flask==2.2.5
- PyPDF2==3.0.1
- gTTS==2.2.3
- Flask-SocketIO==5.1.0

You can install these dependencies using `pip install -r requirements.txt`.

## Installation

1. Clone this repository:


2. Install the required dependencies:


3. Run the application:


The application should now be accessible at `http://localhost:5000` in your web browser.

## Usage

1. Sign up or log in to the application.
2. Upload a PDF file.
3. Choose the desired voice for the audio output.
4. Click on the "Convert" button to convert the PDF to audio.
5. Once the conversion is complete, you can download the audio file.
6. You can also view and delete your uploaded audio files on the "My Files" page.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

