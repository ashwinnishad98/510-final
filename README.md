# AI Powered News Companion

There are too many sources of information, and sifting through them and identifying whats true vs. what's not true is exhausting. Hence, this project.


### The Solution
I created a simple proof of concept, to showcase an all encompassing news application, leveraging AI to provide summaries, perform sentiment analysis, and perform data visualization of trending topics.

## Getting Started
```
python -m venv venv
source venv venv
pip install -r requirements.txt
cp .sample_env .env
```
Replace the API keys with actual values.

## How to Run
```
streamlit run main.py
```

## File Structure
- main.py: Entry point file that contains sidebar navigation between the home, news visualization and bookmark page.
- home.py: Contains the code that shows news article, with filter options using the date, sentiment, and topic. Also includes a search functionality that can be combined with the filters. Each article has an AI summary, using OpenAI's GPT 3.5 Turbo model, along with a sentiment analysis performed by the model. Key phrases are also presented to the user. Users are also able to bookmark articles to read later.
- news_visualizations.py: A page that contains 4 different visualizations of data regardining present day news topics.
- bookmarks.py: A page dedicated to showing all bookmarked articles.
- styles/styles.css: CSS styling shared across all files.
- firebase_config.py: File to initialize Firebase, to use firestore database to store bookmarked articles.

## Technologies Used
- Streamlit
- OpenAI GPT 3.5 Turbo
- CSS Styling
- Firebase Firestore Database
- Bureau of Labor Statistics (BLS) API
- Presidential approval data from FiveThirtyEight.com
- Daily stock prices from Alpha Vantage API
- Palestinian Crisis Data from The Humanitarian Data Exchange

## Reflections
- Through this project, I learned how complex it can be to aggregate news information from multiple sources, and present it in a simple and digestable way.
- I learned a lot about visualizing data through methods defined by streamlit and plotly, and it was interesting to see how complex information can be represented in a simple graphical format.

## Problems Faced
- A few issues I ran into was regarding proper parsing of the JSON or response data from API calls. I had to reiterate on how I parsed the data and plotted it.
- Since Streamlit doesn't natively support multiple pages, I had to use a workaround of running `st.rerun()` to handle the functionality of supporting multiple pages.