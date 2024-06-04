import streamlit as st
from utils import fetch_news, get_ai_summary, get_sentiment_analysis, get_key_phrases
from datetime import datetime, timedelta

# Define available topics and sentiment options
TOPICS = ['Technology', 'Sports', 'Politics', 'Health', 'Science', 'Entertainment', 'Business', 'World', 'Lifestyle', 'Environment']
DATE_OPTIONS = ["Yesterday", "Last Week", "Last Month"]
SENTIMENT_OPTIONS = ["Positive", "Neutral", "Negative"]

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

def sentiment_box(sentiment):
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

def filter_by_date(articles, date_option):
    if date_option == "Yesterday":
        start_date = datetime.now() - timedelta(days=1)
        end_date = start_date + timedelta(days=1)
    elif date_option == "Last Week":
        start_date = datetime.now() - timedelta(days=datetime.now().weekday() + 7)  # Start of the last week
        end_date = start_date + timedelta(days=7)
    elif date_option == "Last Month":
        start_date = datetime.now().replace(day=1) - timedelta(days=1)  # End of last month
        start_date = start_date.replace(day=1)  # Start of last month
        end_date = datetime.now().replace(day=1)  # Start of the current month
    else:
        return articles

    filtered_articles = [article for article in articles if start_date <= datetime.strptime(article.get('publishedAt', ''), '%Y-%m-%dT%H:%M:%SZ') <= end_date]
    return filtered_articles

def filter_by_sentiment(articles, selected_sentiment):
    if selected_sentiment:
        filtered_articles = []
        for article in articles:
            sentiment = cache_openai_sentiment(article['content'] or article['description'])
            if sentiment.lower() == selected_sentiment.lower():
                filtered_articles.append(article)
        return filtered_articles
    return articles

def fetch_and_filter_news():
    # Fetch news based on search query and selected topics
    if st.session_state.search_query:
        if st.session_state.selected_topics:
            st.markdown(f'<div class="subheader-font">Results for: {st.session_state.search_query} in {", ".join(st.session_state.selected_topics)}</div>', unsafe_allow_html=True)
            combined_query = f"{st.session_state.search_query} AND {' AND '.join(st.session_state.selected_topics)}"
            news_data = fetch_news([combined_query])
        else:
            st.markdown(f'<div class="subheader-font">Results for: {st.session_state.search_query}</div>', unsafe_allow_html=True)
            news_data = fetch_news([st.session_state.search_query])
    else:
        if st.session_state.selected_topics:
            st.markdown(f'<div class="subheader-font">Results for: {", ".join(st.session_state.selected_topics)}</div>', unsafe_allow_html=True)
            news_data = fetch_news(st.session_state.selected_topics)
        else:
            st.markdown('<div class="subheader-font">Trending Topics</div>', unsafe_allow_html=True)
            st.markdown("---")
            news_data = fetch_news(['trending'])

    if news_data.get('status') == 'error':
        st.error(f"Error fetching news: {news_data.get('message')}")
        return []

    articles = news_data.get('articles', [])

    # Apply date filter
    if st.session_state.selected_date:
        articles = filter_by_date(articles, st.session_state.selected_date)

    # Apply sentiment filter
    if st.session_state.selected_sentiment:
        articles = filter_by_sentiment(articles, st.session_state.selected_sentiment)

    return articles

def home():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono&display=swap');

    * {
        font-family: 'Roboto Mono', monospace;
    }
    .big-font {
        font-size: 65px !important;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .subheader-font {
        font-size: 34px !important;
    }
    .stButton>button {
        background-color: #fff;
        color: #000;
        border: 1px solid #000;
        padding: 0.25em 1em;
        border-radius: 0.25em;
    }
    .stButton>button:hover {
        background-color: #007bff;
        color: #fff;
        border: 1px solid #007bff;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="big-font">News.AI</div>', unsafe_allow_html=True)

    # Initialize session state variables
    if 'articles_shown' not in st.session_state:
        st.session_state.articles_shown = 10
    if 'selected_topics' not in st.session_state:
        st.session_state.selected_topics = []
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = ""
    if 'selected_sentiment' not in st.session_state:
        st.session_state.selected_sentiment = ""
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""

    # Filters in a single row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_topics = st.multiselect("Filter by topics", TOPICS)
        if selected_topics:
            st.session_state.selected_topics = selected_topics
        else:
            st.session_state.selected_topics = []

    with col2:
        selected_date = st.selectbox("Filter by date", options=[""] + DATE_OPTIONS, index=0, format_func=lambda x: "Choose an option" if x == "" else x)
        if selected_date:
            st.session_state.selected_date = selected_date
        else:
            st.session_state.selected_date = ""

    with col3:
        selected_sentiment = st.selectbox("Filter by sentiment", options=[""] + SENTIMENT_OPTIONS, index=0, format_func=lambda x: "Choose an option" if x == "" else x)
        if selected_sentiment:
            st.session_state.selected_sentiment = selected_sentiment
        else:
            st.session_state.selected_sentiment = ""

    # Search bar underneath the filters
    search_query = st.text_input("Search for news topics", "")
    if st.button("Search"):
        if search_query:
            st.session_state.search_query = search_query
            st.session_state.articles_shown = 10  # Reset articles shown count on new search
        else:
            st.session_state.search_query = ""

    # Fetch and filter news
    articles = fetch_and_filter_news()

    # Show only the first `articles_shown` articles
    for article in articles[:st.session_state.articles_shown]:
        # Filter out articles with 'removed'
        if any('removed' in str(value).lower() for value in article.values()):
            continue

        # Format the published date
        published_at = article.get('publishedAt', '')
        if published_at:
            try:
                published_date = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
                formatted_date = published_date.strftime('%B %d, %Y')
            except ValueError:
                formatted_date = published_at
        else:
            formatted_date = "Unknown"

        st.subheader(article['title'])
        st.markdown(f"[Source: {article['source']['name']}]({article['url']})")
        st.write(f"Published at: {formatted_date}")
        if article.get('urlToImage'):
            st.image(article['urlToImage'], width=700)

        # AI-generated summary
        summary = cache_openai_summary(article['content'] or article['description'])
        st.write(f"**Summary:** {summary}")

        # Sentiment analysis
        sentiment = cache_openai_sentiment(article['content'] or article['description'])
        st.markdown(sentiment_box(sentiment), unsafe_allow_html=True)

        # Key phrase extraction
        key_phrases = cache_openai_key_phrases(article['content'] or article['description'])
        st.write(f"**Key Phrases:** {key_phrases}")

        st.markdown("---")

    # Show more button
    if st.session_state.articles_shown < len(articles):
        if st.button("Show More"):
            st.session_state.articles_shown += 10
            st.rerun()  # Rerun to update the displayed articles

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    home()
