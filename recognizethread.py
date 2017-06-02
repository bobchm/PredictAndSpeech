import threading
import requests
import win32com.client
import json
import speech_recognition as sr

MY_EMAIL = "bob.cunningham@tobiidynavox.com"
TALKEY_TOKEN = "LrP9mYDhCbdFOzIIQEfH/E+XtvRUbqzSBSaZdOF07N512kJSV8H/i1TTxMUNIfCu"
FLUENTY_API_URL = 'https://api.fluenty.co/talkey/reply'
NOTHING = "foo"

class recognizeThread (threading.Thread):
    def __init__(self, callbk):
        threading.Thread.__init__(self)
        self.callbk = callbk
        
    def run(self):
        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = False
        while (not recognizerStop):
            spoken = self.listen_text(recognizer)
            if (len(spoken) > 0):
                responses = self.get_responses(spoken)
                self.callbk(spoken, responses)

    def recognize_text_google(self, recognizer, audio):
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            print("Google could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google service; {0}".format(e))
        return ""

    def listen_text(self, recognizer):
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source, timeout=5.0)
            except sr.WaitTimeoutError:
                return ""
        return self.recognize_text_google(recognizer, audio)

    def get_responses(self, spoken):
        ttest = {"email": MY_EMAIL,
                 "token": TALKEY_TOKEN, "text": spoken,
                 "reply": "api access"}
        resp = requests.post(FLUENTY_API_URL, json=ttest)
        responses = []
        if resp.status_code != 200:
            raise print('GET /tasks/ {}'.format(resp.status_code))
        else:
            parsed_json = resp.json()
            try:
                responses = parsed_json['pages'][0]['value']
            except KeyError:
                responses = []
        return responses


def startRecognizer(cb):
    global recognizerStop
    recognizerStop = False
    thread = recognizeThread(cb)
    thread.start()
    return thread

def killRecognizer(recogThread):
    global recognizerStop
    recognizerStop = True
    recogThread.join()
    
