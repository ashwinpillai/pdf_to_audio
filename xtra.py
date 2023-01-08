from PyPDF2 import PdfReader
import pyttsx3

reader = PdfReader("a2.pdf")
number_of_pages = len(reader.pages)

text = ""
for i in range(number_of_pages):
    page = reader.pages[i]
    text += page.extract_text()

#print(text)

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id) # 1 = female voice ,  0 = male voice
#engine.say(text)  #actually saying the time
engine.save_to_file(text, 'audio.mp3')
engine.runAndWait()