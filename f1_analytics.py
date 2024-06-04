import streamlit as st
from datetime import datetime, timedelta
import pytz
import os
import pandas as pd
import fastf1 as ff1
from utils import get_driver_standings, get_constructor_standings, fetch_news

def enable_cache(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    ff1.Cache.enable_cache(directory)

# Function to fetch the next race details
def get_next_race():
    schedule = ff1.get_event_schedule(2024)
    current_date = pd.to_datetime(datetime.now().date())
    next_race = schedule[schedule['EventDate'] >= current_date].iloc[0]
    return next_race

def format_time_with_suffix(dt):
    suffix = 'th'
    if dt.day in [1, 21, 31]:
        suffix = 'st'
    elif dt.day in [2, 22]:
        suffix = 'nd'
    elif dt.day in [3, 23]:
        suffix = 'rd'
    return dt.strftime(f'%H:%M PST, %B {dt.day}{suffix}, %Y')

def f1_analytics():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono&display=swap');
    * {
        font-family: 'Roboto Mono', monospace;
    }
    .big-font {
        font-size: 50px !important;
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
    .custom-table {
        font-family: 'Roboto Mono', monospace;
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="big-font">Formula 1 Dashboard</div>', unsafe_allow_html=True)

    toggle_option = st.selectbox("Choose View", ["At A Glance", "F1 News"])

    if toggle_option == "At A Glance":
        st.subheader("Next Race Details")
        # Fetch next race details
        next_race = get_next_race()
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("### Next Race")
            st.write(next_race['EventName'])
            st.write(next_race['Country'])
            st.write(next_race['Location'])

        with col2:
            st.write("### Time")
            qualifying_time_utc = next_race['Session4DateUtc']
            race_time_utc = next_race['Session5DateUtc']

            # Convert UTC to Pacific Time
            utc_zone = pytz.utc
            pst_zone = pytz.timezone('America/Los_Angeles')

            qualifying_time = utc_zone.localize(qualifying_time_utc).astimezone(pst_zone)
            race_time = utc_zone.localize(race_time_utc).astimezone(pst_zone)

            st.write(f"Qualifying: {format_time_with_suffix(qualifying_time)}")
            st.write(f"Race: {format_time_with_suffix(race_time)}")

        st.subheader("Driver Standings")
        driver_standings = get_driver_standings()
        driver_standings_data = []
        for driver in driver_standings:
            driver_standings_data.append([driver['position'], driver['Driver']['familyName'], driver['points']])
        driver_df = pd.DataFrame(driver_standings_data, columns=['Position', 'Driver', 'Points'])

        if 'show_all_drivers' not in st.session_state:
            st.session_state.show_all_drivers = False

        if st.session_state.show_all_drivers:
            st.dataframe(driver_df.style.set_table_styles([{
                'selector': 'th',
                'props': [('font-size', '22px'), ('font-family', 'Roboto Mono'), ('text-align', 'center')]
            }, {
                'selector': 'td',
                'props': [('font-size', '22px'), ('font-family', 'Roboto Mono'), ('text-align', 'center')]
            }]), hide_index=True, use_container_width=True)
        else:
            st.dataframe(driver_df.head(10).style.set_table_styles([{
                'selector': 'th',
                'props': [('font-size', '22px'), ('font-family', 'Roboto Mono'), ('text-align', 'center')]
            }, {
                'selector': 'td',
                'props': [('font-size', '22px'), ('font-family', 'Roboto Mono'), ('text-align', 'center')]
            }]), hide_index=True, use_container_width=True)

        if st.button("Show All Drivers"):
            st.session_state.show_all_drivers = True
            st.experimental_rerun()

        st.subheader("Constructor Standings")
        constructor_standings = get_constructor_standings()
        constructor_standings_data = []
        for constructor in constructor_standings:
            constructor_standings_data.append([constructor['position'], constructor['Constructor']['name'], constructor['points']])
        constructor_df = pd.DataFrame(constructor_standings_data, columns=['Position', 'Team', 'Points'])
        st.dataframe(constructor_df.style.set_table_styles([{
            'selector': 'th',
            'props': [('font-size', '22px'), ('font-family', 'Roboto Mono'), ('text-align', 'center')]
        }, {
            'selector': 'td',
            'props': [('font-size', '22px'), ('font-family', 'Roboto Mono'), ('text-align', 'center')]
        }]), hide_index=True, use_container_width=True)

    elif toggle_option == "F1 News":
        st.subheader("Latest F1 News")
        news_data = fetch_news(["Formula 1"])
        articles = news_data.get('articles', [])
        for article in articles:
            st.subheader(article['title'])
            st.write(article['description'])
            st.markdown(f"[Source: {article['source']['name']}]({article['url']})")
            if article.get('urlToImage'):
                st.image(article['urlToImage'], width=700)
            st.write("---")

if __name__ == "__main__":
    f1_analytics()
