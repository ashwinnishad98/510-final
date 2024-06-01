import streamlit as st
from utils import fetch_news

def personalized_feed():
    st.title("Personalized News Feed")
    if 'interests' not in st.session_state:
        st.write("Please set up your profile first.")
    else:
        news_data = fetch_news(st.session_state.interests)
        articles = news_data.get('articles', [])

        for article in articles:
            st.subheader(article['title'])
            st.write(article['description'])
            st.write(f"Source: {article['source']['name']}")
            st.write(f"Published at: {article['publishedAt']}")
            if article.get('urlToImage'):
                st.image(article['urlToImage'], width=700)
            st.write(f"[Read more]({article['url']})")
            st.markdown("---")
