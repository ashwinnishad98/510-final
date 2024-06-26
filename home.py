import streamlit as st
from utils import (
    fetch_news,
    get_ai_summary,
    get_sentiment_analysis,
    get_key_phrases,
    save_article_to_firestore,
    sentiment_box,
    key_phrase_box,
)
from datetime import datetime, timedelta

# available topics and sentiment options
TOPICS = [
    "Technology",
    "Sports",
    "Politics",
    "Health",
    "Science",
    "Entertainment",
    "Business",
    "World",
    "Lifestyle",
    "Environment",
]

# available filters
DATE_OPTIONS = ["Yesterday", "Last Week", "Last Month"]
SENTIMENT_OPTIONS = ["Positive", "Neutral", "Negative"]


# load CSS file
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Cache OpenAI results to avoid repeated calls
@st.cache_data(show_spinner=False, ttl=600)
def cache_openai_summary(text):
    return get_ai_summary(text)


@st.cache_data(show_spinner=False, ttl=600)
def cache_openai_sentiment(text):
    return get_sentiment_analysis(text)


@st.cache_data(show_spinner=False, ttl=600)
def cache_openai_key_phrases(text):
    return get_key_phrases(text)


def save_article_callback(title, url):
    st.write(save_article_to_firestore(title, url))


from datetime import datetime, timedelta


def filter_by_date(articles, date_option):
    """
    Filter a list of articles based on a given date option.

    Args:
        articles (list): A list of articles.
        date_option (str): The date option to filter by. Valid options are "Yesterday", "Last Week", and "Last Month".

    Returns:
        list: A filtered list of articles based on the given date option.
    """
    if date_option == "Yesterday":
        start_date = datetime.now() - timedelta(days=1)
        end_date = start_date + timedelta(days=1)
    elif date_option == "Last Week":
        start_date = datetime.now() - timedelta(
            days=datetime.now().weekday() + 7
        )
        end_date = start_date + timedelta(days=7)
    elif date_option == "Last Month":
        start_date = datetime.now().replace(day=1) - timedelta(
            days=1
        )
        start_date = start_date.replace(day=1)
        end_date = datetime.now().replace(day=1)
    else:
        return articles

    filtered_articles = [
        article
        for article in articles
        if start_date
        <= datetime.strptime(article.get("publishedAt", ""), "%Y-%m-%dT%H:%M:%SZ")
        <= end_date
    ]
    return filtered_articles


def filter_by_sentiment(articles, selected_sentiment):
    """
    Filters a list of articles based on the selected sentiment.

    Args:
        articles (list): A list of articles.
        selected_sentiment (str): The selected sentiment to filter by [Positive, Negative, Neutral].

    Returns:
        list: A filtered list of articles based on the selected sentiment.
    """
    if selected_sentiment:
        filtered_articles = []
        for article in articles:
            sentiment = cache_openai_sentiment(
                article["content"] or article["description"]
            )
            if sentiment.lower() == selected_sentiment.lower():
                filtered_articles.append(article)
        return filtered_articles
    return articles


def fetch_and_filter_news():
    """
    Fetches news articles based on the search query and selected topics, and applies filters based on date and sentiment.

    Returns:
        A list of news articles that match the search query and selected topics, and pass the date and sentiment filters.
    """
    if st.session_state.search_query:
        if st.session_state.selected_topics:
            st.markdown(
                f'<div class="subheader-font">Results for: {st.session_state.search_query} in {", ".join(st.session_state.selected_topics)}</div>',
                unsafe_allow_html=True,
            )
            combined_query = f"{st.session_state.search_query} AND {' AND '.join(st.session_state.selected_topics)}"
            news_data = fetch_news([combined_query])
        else:
            st.markdown(
                f'<div class="subheader-font">Results for: {st.session_state.search_query}</div>',
                unsafe_allow_html=True,
            )
            news_data = fetch_news([st.session_state.search_query])
    else:
        if st.session_state.selected_topics:
            st.markdown(
                f'<div class="subheader-font">Results for: {", ".join(st.session_state.selected_topics)}</div>',
                unsafe_allow_html=True,
            )
            news_data = fetch_news(st.session_state.selected_topics)
        else:
            st.markdown(
                '<div class="subheader-font">Trending Topics</div>',
                unsafe_allow_html=True,
            )
            st.markdown("---")
            news_data = fetch_news(["trending"])

    if news_data.get("status") == "error":
        st.error(f"Error fetching news: {news_data.get('message')}")
        return []

    articles = news_data.get("articles", [])

    if st.session_state.selected_date:
        articles = filter_by_date(articles, st.session_state.selected_date)

    if st.session_state.selected_sentiment:
        articles = filter_by_sentiment(articles, st.session_state.selected_sentiment)

    return articles


def home():
    local_css("styles/styles.css")
    st.markdown('<div class="big-font">News.AI</div>', unsafe_allow_html=True)

    # init session state variables
    if "articles_shown" not in st.session_state:
        st.session_state.articles_shown = 10
    if "selected_topics" not in st.session_state:
        st.session_state.selected_topics = []
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = ""
    if "selected_sentiment" not in st.session_state:
        st.session_state.selected_sentiment = ""
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""

    # display filters in a single row
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_topics = st.multiselect("Filter by topics", TOPICS)
        if selected_topics:
            st.session_state.selected_topics = selected_topics
        else:
            st.session_state.selected_topics = []

    with col2:
        selected_date = st.selectbox(
            "Filter by date",
            options=[""] + DATE_OPTIONS,
            index=0,
            format_func=lambda x: "Choose an option" if x == "" else x,
        )
        if selected_date:
            st.session_state.selected_date = selected_date
        else:
            st.session_state.selected_date = ""

    with col3:
        selected_sentiment = st.selectbox(
            "Filter by sentiment",
            options=[""] + SENTIMENT_OPTIONS,
            index=0,
            format_func=lambda x: "Choose an option" if x == "" else x,
        )
        if selected_sentiment:
            st.session_state.selected_sentiment = selected_sentiment
        else:
            st.session_state.selected_sentiment = ""

    # search bar
    search_query = st.text_input("Search for news topics", "")
    if st.button("Search"):
        if search_query:
            st.session_state.search_query = search_query
            st.session_state.articles_shown = 10
        else:
            st.session_state.search_query = ""

    articles = fetch_and_filter_news()

    # show first 10 articles
    for index, article in enumerate(articles[: st.session_state.articles_shown]):

        # filter out articles with 'removed'
        if any("removed" in str(value).lower() for value in article.values()):
            continue

        published_at = article.get("publishedAt", "")
        if published_at:
            try:
                published_date = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
                formatted_date = published_date.strftime("%B %d, %Y")
            except ValueError:
                formatted_date = published_at
        else:
            formatted_date = "Unknown"

        st.subheader(article["title"])
        st.markdown(f"[Source: {article['source']['name']}]({article['url']})")
        st.markdown(f"Published at: {formatted_date} <br>", unsafe_allow_html=True)

        if st.button(f"Bookmark", key=f"bookmark_{index}"):
            save_article_callback(article["title"], article["url"])

        if article.get("urlToImage"):
            st.image(article["urlToImage"], width=700)

        summary = cache_openai_summary(article["content"] or article["description"])
        st.write(f"**Summary:** {summary}")

        sentiment = cache_openai_sentiment(article["content"] or article["description"])
        st.markdown(sentiment_box(sentiment), unsafe_allow_html=True)

        key_phrases = cache_openai_key_phrases(
            article["content"] or article["description"]
        )
        key_phrases_list = key_phrases.split(", ")
        st.write(f"**Key Phrases**")
        st.markdown(key_phrase_box(key_phrases_list), unsafe_allow_html=True)

        st.markdown("---")

        # callback function to save article to firestore
        st.session_state[f"save_article_callback_{index}"] = (
            lambda title=article["title"], url=article["url"]: save_article_callback(
                title, url
            )
        )

    if st.session_state.articles_shown < len(articles):
        if st.button("Show More"):
            st.session_state.articles_shown += 10
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    home()
