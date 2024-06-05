import streamlit as st
import requests
from openai import OpenAI
from datetime import datetime
import requests
from firebase_config import initialize_firebase


db = initialize_firebase()

# API Key for NewsAPI and OpenAI
NEWS_API_KEY = st.secrets("NEWS_API_KEY")
OPENAI_API_KEY = st.secrets("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


def fetch_news(topics):
    """
    Fetches news articles based on the given topics.

    Args:
        topics (list): A list of topics to search for news articles. If no topics are provided, the default topic is "general".

    Returns:
        dict: A dictionary containing the JSON response from the News API.

    """
    if not topics:
        topics = ["general"]
    query = " OR ".join(topics)
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    return response.json()


def fetch_trending_topics():
    """
    Fetches the trending topics from the News API.

    Returns:
        dict: A dictionary containing the response from the News API.
            If the request is successful, the dictionary will contain the trending topics.
            If the request fails, the dictionary will contain an error status, code, and message.
    """
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}&pageSize=10"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "status": "error",
            "code": response.status_code,
            "message": response.text,
        }


def get_ai_summary(text):
    """
    Generates an AI summary of the given text using OpenAI's GPT-3.5 Turbo model.

    Parameters:
    text (str): The text to be summarized.

    Returns:
    str: The generated summary of the text.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an expert reader. Summarize the following article to capture all the high level information, in a concise and succint manner.",
            },
            {"role": "user", "content": text},
        ],
    )
    summary = response.choices[0].message.content.strip()
    return summary


def get_sentiment_analysis(text):
    """
    Analyzes the sentiment of the given text and returns whether it's Positive, Negative, or Neutral.

    Args:
        text (str): The text to be analyzed.

    Returns:
        str: The sentiment of the text (Positive, Negative, or Neutral).
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Analyze the sentiment of the following text. Only return whether it's Positive, Negative, or Neutral, nothing else.",
            },
            {"role": "user", "content": text},
        ],
    )
    sentiment = response.choices[0].message.content.strip()
    if sentiment.lower() not in ["positive", "negative", "neutral"]:
        sentiment = "Neutral"
    return sentiment


def get_key_phrases(text):
    """
    Extracts key phrases from the given text using OpenAI's GPT-3.5 Turbo model.

    Args:
        text (str): The input text from which key phrases need to be extracted.

    Returns:
        str: A string containing the top five key phrases separated by commas.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Extract key phrases from the following text. Return five comma separated key phrases.",
            },
            {"role": "user", "content": text},
        ],
    )
    key_phrases = response.choices[0].message.content.strip().split("\n")
    key_phrases = [phrase.strip() for phrase in key_phrases if phrase.strip()]

    key_phrases = key_phrases[:5]
    return ", ".join(key_phrases)


def save_article_to_firestore(title, url):
    """
    Saves an article to Firestore if it doesn't already exist.

    Args:
        title (str): The title of the article.
        url (str): The URL of the article.

    Returns:
        str: A message indicating whether the article was bookmarked successfully or if it already exists.
    """
    # check if the article already exists
    articles_ref = db.collection("saved_articles")
    query = articles_ref.where("title", "==", title).where("link", "==", url).limit(1)
    existing_articles = query.stream()

    if any(existing_articles):
        return "Article already bookmarked."

    doc_ref = db.collection("saved_articles").document()
    doc_ref.set({"title": title, "link": url, "timestamp": datetime.now()})

    return "Article bookmarked successfully!"


def fetch_bookmarked_articles():
    """
    Fetches and returns a list of bookmarked articles from the database.

    Returns:
        A list of dictionaries, where each dictionary represents an article with the following keys:
        - "title": The title of the article.
        - "link": The link to the article.
        - "timestamp": The timestamp when the article was bookmarked.
    """
    articles_ref = db.collection("saved_articles").order_by(
        "timestamp", direction="DESCENDING"
    )
    articles = articles_ref.stream()
    return [
        {
            "title": article.get("title"),
            "link": article.get("link"),
            "timestamp": article.get("timestamp"),
        }
        for article in articles
    ]


def sentiment_box(sentiment):
    """
    Generates an HTML div element representing a sentiment box.

    Args:
        sentiment (str): The sentiment value ("positive", "negative", or any other value for neutral).

    Returns:
        str: The HTML representation of the sentiment box.

    """
    if sentiment.lower() == "positive":
        color = "#4CAF50"
    elif sentiment.lower() == "negative":
        color = "#F44336"
    else:
        color = "#FFA500"  # Orange for neutral
    return f"""
    <div style='
        background-color: {color};
        color: white;
        padding: 5px 10px;
        border-radius: 10px;
        display: inline-block;
        font-weight: bold;
        margin-bottom: 15px;
    '>
        {sentiment.capitalize()}
    </div>
    """


def key_phrase_box(key_phrases):
    """
    Generates HTML code for displaying key phrases in styled boxes.

    Args:
        key_phrases (list): A list of key phrases to be displayed.

    Returns:
        str: HTML code representing the styled boxes containing the key phrases.
    """
    boxes = []
    for phrase in key_phrases:
        box = f"""
        <div style='
            background-color: #333333;
            color: white;
            padding: 5px 10px;
            border-radius: 10px;
            display: inline-block;
            font-weight: bold;
            margin-right: 5px;
            margin-bottom: 15px;
        '>
            {phrase}
        </div>
        """
        boxes.append(box)
    all_boxes = "".join(boxes)
    return all_boxes
