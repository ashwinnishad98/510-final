import streamlit as st
from utils import (
    get_ai_summary,
    get_sentiment_analysis,
    get_key_phrases,
    fetch_bookmarked_articles,
    sentiment_box,
    key_phrase_box,
)


# Load CSS file
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


def display_bookmarked_articles():
    local_css("styles/styles.css")
    st.markdown(
        '<div class="big-font">Bookmarked Articles</div>', unsafe_allow_html=True
    )

    articles = fetch_bookmarked_articles()

    for index, article in enumerate(articles):
        st.subheader(article["title"])
        st.markdown(f"[Read more]({article['link']})")
        st.markdown(
            f"Bookmarked at: {article['timestamp'].strftime('%B %d, %Y')} <br>",
            unsafe_allow_html=True,
        )

        # Fetch and display AI-generated summary, sentiment, and key phrases
        content = (
            f"Content of the article titled '{article['title']}'"  # Placeholder content
        )
        summary = cache_openai_summary(content)
        st.write(f"**Summary:** {summary}")

        sentiment = cache_openai_sentiment(content)
        st.markdown(sentiment_box(sentiment), unsafe_allow_html=True)

        key_phrases = cache_openai_key_phrases(content)
        key_phrases_list = key_phrases.split(", ")
        st.write(f"**Key Phrases**")
        st.markdown(key_phrase_box(key_phrases_list), unsafe_allow_html=True)

        st.markdown("---")


if __name__ == "__main__":
    display_bookmarked_articles()
