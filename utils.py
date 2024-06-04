import os
from dotenv import load_dotenv
import requests
from openai import OpenAI
import requests

# Load environment variables from .env file
load_dotenv()

# API Key for NewsAPI and OpenAI
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

BASE_URL = "https://ergast.com/api/f1"


def fetch_news(topics):
    if not topics:
        topics = ['general']
    query = ' OR '.join(topics)
    url = f'https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    return response.json()

def fetch_trending_topics():
    url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}&pageSize=10'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {'status': 'error', 'code': response.status_code, 'message': response.text}

def get_ai_summary(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Summarize the following article."},
            {"role": "user", "content": text}
        ]
    )
    summary = response.choices[0].message.content.strip()
    return summary

def get_sentiment_analysis(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Analyze the sentiment of the following text. Only return whether it's Positive, Negative, or Neutral, nothing else."},
            {"role": "user", "content": text}
        ]
    )
    sentiment = response.choices[0].message.content.strip()
    # Ensure only the sentiment word is returned
    if sentiment.lower() not in ["positive", "negative", "neutral"]:
        sentiment = "Neutral"
    return sentiment

def get_key_phrases(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Extract key phrases from the following text. Return a list of key phrases, up to 5."},
            {"role": "user", "content": text}
        ]
    )
    key_phrases = response.choices[0].message.content.strip().split('\n')
    key_phrases = [phrase.strip() for phrase in key_phrases if phrase.strip()]
    # Ensure only up to 5 key phrases are returned
    key_phrases = key_phrases[:5]
    return ', '.join(key_phrases)

def get_driver_standings(season="current"):
    url = f"{BASE_URL}/{season}/driverStandings.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
    else:
        return []

def get_constructor_standings(season="current"):
    url = f"{BASE_URL}/{season}/constructorStandings.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
    else:
        return []