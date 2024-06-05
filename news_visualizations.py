import streamlit as st
import requests
import os
import pandas as pd
import plotly.express as px


BLS_API_KEY = st.secrets("BLS_API_KEY")
STOCKS_API_KEY = st.secrets("STOCKS_API_KEY")


# load CSS file
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


@st.cache_data(show_spinner=True, ttl=3600)  # cache the data for an hour
def get_inflation_data():
    """
    Retrieves inflation data from the Bureau of Labor Statistics (BLS) API and returns it as a DataFrame.

    Returns:
        df (pandas.DataFrame): DataFrame containing the inflation data.
    """
    series_id = "CUSR0000SA0"  # series ID for Consumer Price Index
    api_key = BLS_API_KEY
    url = f"https://api.bls.gov/publicAPI/v2/timeseries/data/{series_id}?registrationkey={api_key}"
    response = requests.get(url)
    data = response.json()

    series_data = data["Results"]["series"][0]["data"]

    df = pd.DataFrame(series_data)

    df["date"] = pd.to_datetime(
        df["year"] + df["period"].str.replace("M", ""), format="%Y%m"
    )

    df = df.sort_values("date")

    df = df.reset_index(drop=True)

    return df


@st.cache_data(show_spinner=True, ttl=3600)
def get_presidential_approval_data():
    """
    Retrieves presidential approval data from a CSV file and returns a filtered DataFrame.

    Returns:
        pandas.DataFrame: A DataFrame containing the filtered presidential approval data.
    """
    url = "https://projects.fivethirtyeight.com/polls-page/data/president_polls.csv"
    data = pd.read_csv(url)

    data["end_date"] = pd.to_datetime(data["end_date"])

    data = data[
        (data["candidate_name"].isin(["Donald Trump", "Joe Biden"]))
        & (data["end_date"].dt.year.isin([2020, 2021, 2022, 2023, 2024]))
    ]

    data = data[["end_date", "candidate_name", "pct"]]

    return data


@st.cache_data(show_spinner=True, ttl=3600)
def get_stock_data():
    """
    Retrieves daily stock data for a given symbol from Alpha Vantage API.

    Returns:
    pandas.DataFrame: A DataFrame containing the daily stock data with columns for open, high, low, close, and volume.
    """
    symbol = "AAPL"
    api_key = STOCKS_API_KEY
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    time_series = data["Time Series (Daily)"]

    df = pd.DataFrame.from_dict(time_series, orient="index", dtype="float")
    df.index = pd.to_datetime(df.index)

    df.columns = ["open", "high", "low", "close", "volume"]

    df = df.sort_index()

    return df


@st.cache_data(show_spinner=True, ttl=3600)
def get_palestinian_death_toll_data():
    """
    Retrieves the Palestinian death toll data from a specified URL and returns it as a pandas DataFrame.

    Returns:
        pandas.DataFrame: The Palestinian death toll data.
    """
    url = "https://data.humdata.org/dataset/a02d750c-b2f7-4e22-b884-e9e495209a3a/resource/429619ed-8b50-4a01-a2b3-88601bc606ce/download/opt_-escalation-of-hostilities-impact-4-1-1-1-1-1.xlsx"
    gaza_data = pd.read_excel(url, sheet_name="Gaza")

    gaza_data["date"] = pd.to_datetime(gaza_data["date"], format="%d-%b-%Y")

    return gaza_data


def plot_death_toll_data(df, region):
    """
    Plots the death toll data for a given region.

    Args:
        df (DataFrame): The DataFrame containing the death toll data.
        region (str): The name of the region.

    Returns:
        fig (plotly.graph_objects.Figure): The plotly figure object representing the death toll visualization.
    """
    # melt the df for better plotting
    df_melted = df.melt(
        id_vars=["date"],
        value_vars=["killed total", "killed female", "killed male", "killed undefined"],
        var_name="Category",
        value_name="Deaths",
    )

    fig = px.line(
        df_melted,
        x="date",
        y="Deaths",
        color="Category",
        title=f"Death Toll in {region}",
        labels={"date": "Date", "Deaths": "Number of Deaths"},
        color_discrete_map={
            "killed total": "red",
            "killed female": "pink",
            "killed male": "blue",
            "killed undefined": "green",
        },
    )
    return fig


# page layout and content
def news_visualizations():
    local_css("styles/styles.css")

    st.markdown(
        '<div class="big-font">News Visualization</div>', unsafe_allow_html=True
    )

    st.header("1. Inflation in America")
    inflation_data = get_inflation_data()
    fig = px.line(
        inflation_data,
        x="date",
        y="value",
        title="Inflation in America (CPI)",
        labels={"value": "CPI Value", "date": "Date"},
    )
    st.plotly_chart(fig)

    st.markdown("---")

    st.header("2. Presidential Candidate Approval Ratings")
    approval_data = get_presidential_approval_data()

    if (
        "end_date" not in approval_data.columns
        or "pct" not in approval_data.columns
        or "candidate_name" not in approval_data.columns
    ):
        st.error("Data does not have the required columns.")
        return

    # color map for the candidates
    color_map = {"Donald Trump": "red", "Joe Biden": "blue"}

    # moving average to smooth the data
    approval_data["smoothed_pct"] = approval_data.groupby("candidate_name")[
        "pct"
    ].transform(lambda x: x.rolling(window=30, min_periods=1).mean())

    fig = px.line(
        approval_data,
        x="end_date",
        y="smoothed_pct",
        color="candidate_name",
        title="Presidential Candidate Approval Ratings",
        labels={"smoothed_pct": "Approval Rating (%)", "end_date": "Date"},
        color_discrete_map=color_map,
    )
    if fig:
        st.plotly_chart(fig)

    st.markdown("---")

    st.header("3. Stock Price of Apple")
    stock_data = get_stock_data()
    fig = px.line(
        stock_data,
        x=stock_data.index,
        y="close",
        title="Apple Stock Price",
        labels={"close": "Close Price", "index": "Date"},
    )

    st.plotly_chart(fig)

    st.markdown("---")

    st.header("4. Palestinian Death Toll Over the Last Year")
    gaza_data = get_palestinian_death_toll_data()
    gaza_fig = plot_death_toll_data(gaza_data, "Gaza")
    st.plotly_chart(gaza_fig)


if __name__ == "__main__":
    news_visualizations()
