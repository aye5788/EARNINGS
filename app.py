import streamlit as st
import requests
import pandas as pd

# Load API Token securely from Streamlit Secrets
API_TOKEN = st.secrets["orats"]["api_token"]
BASE_URL = "https://api.orats.io/datav2/cores"

# Function to fetch earnings move data from ORATS API
def fetch_earnings_data(ticker):
    params = {
        "token": API_TOKEN,
        "ticker": ticker
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            return data[0]  # Return the first (and typically only) record
        else:
            st.warning("No data found for the specified ticker.")
            return None
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

# Streamlit App UI
st.title("📊 Earnings Move Dashboard")
st.write("Enter a stock ticker to fetch its implied and historical earnings moves.")

# User input for ticker
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, MSFT)", value="AAPL").upper()

# Fetch and display data
if st.button("Get Earnings Data"):
    with st.spinner("Fetching data..."):
        earnings_data = fetch_earnings_data(ticker)
        if earnings_data:
            imp_earn_mv = earnings_data.get("impErnMv")
            abs_avg_earn_mv = earnings_data.get("absAvgErnMv")
            next_earn_date = earnings_data.get("nextErn")
            historical_moves = {f"ernMv{i}": earnings_data.get(f"ernMv{i}") for i in range(1, 13)}

            # Display fetched data
            st.subheader(f"📌 Data for {ticker}")
            st.metric("📈 Current Implied Earnings Move", f"{imp_earn_mv}%")
            st.metric("📉 Average Historical Earnings Move", f"{abs_avg_earn_mv}%")
            st.metric("📅 Next Earnings Date", next_earn_date)

            # Historical Earnings Moves Table
            df = pd.DataFrame(list(historical_moves.items()), columns=["Earnings Move", "Percentage"])
            df["Earnings Move"] = df["Earnings Move"].str.replace("ernMv", "Earnings #")
            st.table(df)

