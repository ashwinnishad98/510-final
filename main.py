import streamlit as st
from home import home
from f1_analytics import f1_analytics

# Main function to control the navigation
def main():
    # Render the sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Formula 1 Analytics"])
    
    if page == "Home":
        home()
    elif page == "Formula 1 Analytics":
        f1_analytics()

if __name__ == "__main__":
    main()
