import tkinter

import configparser
import pressagio.callback
import pressagio

import threading
import recognizethread

import win32com.client
import stopwords
import re

# Define and create PresageCallback object
class DemoCallback(pressagio.callback.Callback):
    def __init__(self, buffer):
        super().__init__()
        self.buffer = buffer

    def past_stream(self):
        return self.buffer

    def future_stream(self):
        return ''

class simpleapp_tk(tkinter.Tk):
    def __init__(self,parent):
        tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.grid()
        self.speaker = win32com.client.Dispatch("SAPI.SpVoice")

        self.entryVariable = tkinter.StringVar()
        self.entry = tkinter.Entry(self,textvariable=self.entryVariable)
        self.entry.grid(column=0,row=0,sticky='EW')
        self.entry.bind("<Return>", self.OnPressEnter)
        self.entryVariable.set(u"Enter text here.")

        self.clearButton = tkinter.Button(self,text=u"Clear", width = 15, command=self.OnClearButton)
        self.clearButton.grid(column=1,row=0)

        self.speakButton = tkinter.Button(self,text=u"Speak", width = 15, command=self.OnSpeakButton)
        self.speakButton.grid(column=2,row=0)

        # Predictor Buttons
        lbl = tkinter.Label(self, text="Predictions")
#        lbl.pack()
        lbl.grid(column=0,row=1)

        self.p1Text = tkinter.StringVar()
        self.p1Text.set("")
        self.p1Button = tkinter.Button(self, textvariable = self.p1Text,font=("Times", 12), width = 30, borderwidth = 1, command=self.OnP1Click)
        self.p1Button.grid(column=0,row=2)

        self.p2Text = tkinter.StringVar()
        self.p2Text.set("")
        self.p2Button = tkinter.Button(self, textvariable = self.p2Text,font=("Times", 12), width = 30, borderwidth = 1, command=self.OnP2Click)
        self.p2Button.grid(column=1,row=2)

        self.p3Text = tkinter.StringVar()
        self.p3Text.set("")
        self.p3Button = tkinter.Button(self, textvariable = self.p3Text,font=("Times", 12), width = 30, borderwidth = 1, command=self.OnP3Click)
        self.p3Button.grid(column=2,row=2)

        # Content Word Buttons
        lbl = tkinter.Label(self, text="Content Words")
#        lbl.pack()
        lbl.grid(column=0,row=3)

        self.c1Text = tkinter.StringVar()
        self.c1Text.set("")
        self.c1Button = tkinter.Button(self, textvariable = self.c1Text,font=("Times", 12), width = 30, borderwidth = 1, command=self.OnC1Click)
        self.c1Button.grid(column=0,row=4)

        self.c2Text = tkinter.StringVar()
        self.c2Text.set("")
        self.c2Button = tkinter.Button(self, textvariable = self.c2Text,font=("Times", 12), width = 30, borderwidth = 1, command=self.OnC2Click)
        self.c2Button.grid(column=1,row=4)

        self.c3Text = tkinter.StringVar()
        self.c3Text.set("")
        self.c3Button = tkinter.Button(self, textvariable = self.c3Text,font=("Times", 12), width = 30, borderwidth = 1, command=self.OnC3Click)
        self.c3Button.grid(column=2,row=4)

        # Suggested Response Buttons
        lbl = tkinter.Label(self, text="Responses")
     #   lbl.pack()
        lbl.grid(column=0,row=5)

        self.r1Text = tkinter.StringVar()
        self.r1Text.set("")
        self.r1Button = tkinter.Button(self, textvariable = self.r1Text,font=("Times", 12), width = 30, borderwidth = 1, command=self.OnR1Click)
        self.r1Button.grid(column=0,row=6)

        self.r2Text = tkinter.StringVar()
        self.r2Text.set("")
        self.r2Button = tkinter.Button(self, textvariable = self.r2Text,font=("Times", 12), width = 30, borderwidth = 1, command=self.OnR2Click)
        self.r2Button.grid(column=1,row=6)

        self.r3Text = tkinter.StringVar()
        self.r3Text.set("")
        self.r3Button = tkinter.Button(self, textvariable = self.r3Text,font=("Times", 12), width = 30, borderwidth = 1, command=self.OnR3Click)
        self.r3Button.grid(column=2,row=6)

        self.grid_columnconfigure(0,weight=1)
        self.resizable(True,False)
        self.update()
        self.geometry(self.geometry())
        self.entry.focus_set()
        self.entry.selection_range(0, tkinter.END)

        config_file = "example_profile.ini"
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self.entryVariable.trace("w", self.EntryChangeCallback)        
       
        self.displayLock = threading.Lock()
        self.SetPredictors()
        self.recogThread = recognizethread.startRecognizer(self.RecognizeCallback)

    def OnClearButton(self):
        self.entryVariable.set("")
        self.entry.focus_set()
        self.SetPredictors()

    def OnSpeakButton(self):
        self.speaker.Speak(self.entryVariable.get())

    def OnP1Click(self):
        self.InsertPred(self.p1Text.get())

    def OnP2Click(self):
        self.InsertPred(self.p2Text.get())

    def OnP3Click(self):
        self.InsertPred(self.p3Text.get())

    def OnC1Click(self):
        self.InsertPred(self.c1Text.get())

    def OnC2Click(self):
        self.InsertPred(self.c2Text.get())

    def OnC3Click(self):
        self.InsertPred(self.c3Text.get())

    def OnR1Click(self):
        self.InsertPred(self.r1Text.get())

    def OnR2Click(self):
        self.InsertPred(self.r2Text.get())

    def OnR3Click(self):
        self.InsertPred(self.r3Text.get())

    def InsertPred(self, txt):
        self.entryVariable.set(txt)

    def OnPressEnter(self,event):
        self.entry.focus_set()
        self.entry.selection_range(0, tkinter.END)

    def SetPredictors(self):
        txt = " " + self.entryVariable.get()
        callback = DemoCallback(txt)
        prsgio = pressagio.Pressagio(callback, self.config)
        predictions = prsgio.predict()
        try:
            self.p1Text.set(predictions[0])
        except KeyError:
            self.p1Text.set("")
        try:
            self.p2Text.set(predictions[1])
        except KeyError:
            self.p2Text.set("")
        try:
            self.p3Text.set(predictions[2])
        except KeyError:
            self.p3Text.set("")

    def EntryChangeCallback(self, *args):
        self.SetPredictors()

    def RecognizeCallback(self, utterance, responses):
        self.title("Predicto - " + utterance)
        contentWords = self.GetContentWords(utterance)
        self.SetContentWords(contentWords)
        self.SetResponses(responses)
        
    def SetContentWords(self, words):
        try:
            self.c1Text.set(words[0])
        except IndexError:
            self.c1Text.set("")
        try:
            self.c2Text.set(words[1])
        except IndexError:
            self.c2Text.set("")
        try:
            self.c3Text.set(words[2])
        except IndexError:
            self.c3Text.set("")

    def SetResponses(self, responses):
        try:
            self.r1Text.set(responses[0])
        except IndexError:
            self.r1Text.set("")
        try:
            self.r2Text.set(responses[1])
        except IndexError:
            self.r2Text.set("")
        try:
            self.r3Text.set(responses[2])
        except IndexError:
            self.r3Text.set("")

    def GetContentWords(self, utterance):
        words = re.findall(r"[\w']+", utterance.lower())
        contentWords = []
        for word in words:
            if not word in contentWords and not stopwords.is_stop_word(word):
                contentWords.append(word)
        return contentWords
        
if __name__ == "__main__":
    app = simpleapp_tk(None)
    app.title('Predicto')
    app.mainloop()
    recognizethread.killRecognizer(app.recogThread)
