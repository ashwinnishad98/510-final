import streamlit as st

def user_registration():
    st.title("User Registration")
    user_choice = st.radio("Do you want to sign in or skip?", ('Sign In', 'Skip'))
    if user_choice == 'Sign In':
        user_email = st.text_input("Enter your email")
        if st.button("Save"):
            st.session_state.user = user_email
    else:
        st.session_state.user = 'guest'
