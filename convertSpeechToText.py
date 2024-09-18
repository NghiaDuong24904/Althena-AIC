# pip install SpeechRecognition pyaudio
import speech_recognition as sr

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print('Moi m noi; ')
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language='vi-VN')
            return text
        except sr.UnknownValueError:
            print("Không thể nhận diện giọng nói.")
        except sr.RequestError as e:
            print(f"Không thể kết nối đến dịch vụ nhận diện giọng nói; {e}")
    return ""

#print(recognize_speech_from_mic())