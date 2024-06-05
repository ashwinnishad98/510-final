import streamlit as st
from home import home
from news_visualizations import news_visualizations
from bookmarks import display_bookmarked_articles


# main function to control the navigation
def main():
    """
    Main function that renders the sidebar for navigation and handles page selection.

    The function displays a sidebar with navigation options and based on the selected page,
    it calls the corresponding function to display the content.

    Parameters:
        None

    Returns:
        None
    """
    # Render the sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "News Visualizations", "Bookmarks"])

    if page == "Home":
        home()
    elif page == "News Visualizations":
        news_visualizations()
    elif page == "Bookmarks":
        display_bookmarked_articles()


if __name__ == "__main__":
    main()
