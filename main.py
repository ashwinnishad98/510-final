import streamlit as st
from home import home
from user_registration import user_registration
from profile_setup import profile_setup
from personalized_feed import personalized_feed

# Main function to control the navigation
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "User Registration", "Profile Setup", "Personalized News Feed"])
    
    if page == "Home":
        home()
    elif page == "User Registration":
        user_registration()
    elif page == "Profile Setup":
        profile_setup()
    elif page == "Personalized News Feed":
        personalized_feed()

if __name__ == "__main__":
    main()