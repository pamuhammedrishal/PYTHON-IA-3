import speech_recognition as sr
import pyttsx3
import time
from time import ctime
import webbrowser
import wikipedia
from tkinter import *
import sqlite3
import requests
import json

print('Say something...')
r = sr.Recognizer()
speaker = pyttsx3.init()


class VirtualAssistant:
    def __init__(self):
        self.conn = sqlite3.connect('assistant_data.db')
        self.create_table()
        
        self.root = Tk()
        self.root.title('virtual assistant')
        self.root.geometry('520x320')

        self.userText = StringVar()
        self.userText.set('ASSISTANT HERE ')
        self.userFrame = LabelFrame(self.root, text='thakudu', font=('Railways', 18, 'bold'))
        self.userFrame.pack(fill='both', expand='yes')
        top = Message(self.userFrame, textvariable=self.userText, bg='black', fg='white')
        top.config(font=("Century Gothic", 15, 'bold'))
        top.pack(side='top', fill='both', expand='yes')

        btn = Button(self.root, text='Speak', font=('Railways', 10, 'bold'), bg='red', fg='white', command=self.clicked)
        btn.pack(fill='x', expand='no')
        btn2 = Button(self.root, text='Close', font=('Railways', 10, 'bold'), bg='yellow', fg='black', command=self.root.destroy)
        btn2.pack(fill='x', expand='no')

        self.assistant_speak('How can I help you?')
        self.root.mainloop()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT,
                assistant_response TEXT
            )
        ''')
        self.conn.commit()

    def record_audio(self, ask=False):
        with sr.Microphone() as source:
            if ask:
                self.assistant_speak(ask)
            audio = r.listen(source)
        voice_data = ''
        try:
            voice_data = r.recognize_google(audio)
            print('Recognized voice: ' + voice_data)
        except Exception:
            print('Oo')
        return voice_data

    def assistant_speak(self, text):
        speaker.say(text)
        speaker.runAndWait()
    
    def get_weather(self):
        # Add your OpenWeatherMap API key here
        api_key = "d0e669cf4a93e8cba686223b37b38f79"
        city = "COIMBATORE"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        response = requests.get(url)
        data = response.json()
        if data['cod'] == 200:
            weather_description = data['weather'][0]['description']
            temperature = round(data['main']['temp'] - 273.15, 2)  # Convert from Kelvin to Celsius
            return f"The weather in {city} is {weather_description} with a temperature of {temperature} degrees Celsius."
        else:
            return "Sorry, I couldn't fetch the weather information."
    
    def get_news(self):
        # Add your NewsAPI.org API key here
        api_key = "9e4447535fa9492cbcaa16f0f1a1ba6e"
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
        response = requests.get(url)
        data = response.json()
        if data['status'] == 'ok':
            articles = data['articles']
            news_headlines = [article['title'] for article in articles]
            return "Here are the top news headlines for today:\n" + "\n".join(news_headlines)
        else:
            return "Sorry, I couldn't fetch the news at the moment."

    def clicked(self):
        print("Working...")
        voice_data = self.record_audio().lower()
        self.save_to_database(voice_data, '')
        if 'who are you' in voice_data:
            response = 'My name is thakudu.'
            self.assistant_speak(response)
            self.save_to_database('', response)
        elif 'search' in voice_data:
            search = self.record_audio('What do you want to search for?')
            url = 'https://google.com/search?q=' + search
            webbrowser.get().open(url)
            response = 'Here is what I found for ' + search
            self.assistant_speak(response)
            self.save_to_database(search, response)
        elif 'open youtube' in voice_data:
            self.assistant_speak('Opening YouTube')
            webbrowser.get().open('https://www.youtube.com')
            self.save_to_database('Open YouTube', '')
        elif 'youtube channel' in voice_data:
            channel = self.record_audio('Which YouTube channel are you looking for?')
            url = f'https://www.youtube.com/results?search_query={channel.replace(" ", "+")}'
            webbrowser.get().open(url)
            response = f'Searching YouTube for the channel {channel}'
            self.assistant_speak(response)
            self.save_to_database(channel, response)
        elif 'wikipedia' in voice_data:
            topic = self.record_audio('What do you want to know about?')
            summary = wikipedia.summary(topic, sentences=2)
            response = 'According to Wikipedia: ' + summary
            self.assistant_speak(response)
            self.save_to_database(topic, response)
        elif 'find location' in voice_data:
            location = self.record_audio('What is the location?')
            url = 'https://google.nl/maps/place/' + location + '/&amp;'
            webbrowser.get().open(url)
            response = 'Here is the location for ' + location
            self.assistant_speak(response)
            self.save_to_database(location, response)
        elif 'what is the time' in voice_data:
            response = "The current time is: " + ctime()
            self.assistant_speak(response)
            self.save_to_database('', response)
        elif 'hello' in voice_data:
            response = "Hello! How can I assist you?"
            self.assistant_speak(response)
            self.save_to_database('', response)
        elif 'weather' in voice_data:
            weather_info = self.get_weather()
            self.assistant_speak(weather_info)
        elif 'get weather' in voice_data:
            weather_info = self.get_weather()
            self.assistant_speak(weather_info)
        elif 'news' in voice_data:
            news_info = self.get_news()
            self.assistant_speak(news_info)    
        elif 'how are you' in voice_data:
            response = "I'm doing well, thank you for asking!"
            self.assistant_speak(response)
            self.save_to_database('', response)
        elif 'exit' in voice_data:
            self.assistant_speak('Goodbye!')
            self.save_to_database('Exit', '')
            exit()
        else:
            response = "let me check"
            self.assistant_speak(response)
            self.save_to_database(voice_data, response)
            self.search_web(voice_data)

    def search_web(self, query):
        # Perform a web search using the user's query
        url = 'https://www.google.com/search?q=' + query.replace(" ", "+")
        webbrowser.get().open(url)

    def save_to_database(self, user_input, assistant_response):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO commands (user_input, assistant_response) VALUES (?, ?)', (user_input, assistant_response))
        self.conn.commit()


if __name__ == '__main__':
    assistant = VirtualAssistant()
