import streamlit as st

TOPICS = ['Technology', 'Sports', 'Politics', 'Health', 'Science', 'Entertainment', 'Business', 'World', 'Lifestyle', 'Environment']

def profile_setup():
    st.title("Profile Setup")
    selected_topics = st.multiselect("Choose topics you are interested in:", TOPICS)
    if st.button("Save Interests"):
        st.session_state.interests = selected_topics
