import streamlit as st
import requests
import pandas as pd
import datetime

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
            # Extract key values
            imp_earn_mv = earnings_data.get("impErnMv")
            abs_avg_earn_mv = earnings_data.get("absAvgErnMv")
            next_earn_date = earnings_data.get("nextErn")
            days_to_next_earn = earnings_data.get("daysToNextErn")
            last_earn_date = earnings_data.get("lastErn")
            last_close_price = earnings_data.get("clsPx")  # Get last closing price

            # Fix the next earnings date issue
            if next_earn_date == "0000-00-00" and isinstance(days_to_next_earn, (int, float)):
                if days_to_next_earn > 0 and last_earn_date not in [None, "0000-00-00"]:
                    last_earn_dt = datetime.datetime.strptime(last_earn_date, "%Y-%m-%d")
                    next_earn_dt = last_earn_dt + datetime.timedelta(days=int(days_to_next_earn))
                    next_earn_date = next_earn_dt.strftime("%Y-%m-%d")
                else:
                    next_earn_date = "N/A"

            # Calculate Expected Price Move
            expected_price_change = None
            if imp_earn_mv is not None and last_close_price is not None:
                expected_price_change = (imp_earn_mv / 100) * last_close_price

            # Extract historical earnings moves
            historical_moves = {f"Earnings #{i}": earnings_data.get(f"ernMv{i}") for i in range(1, 13)}

            # Display fetched data
            st.subheader(f"📌 Data for {ticker}")
            st.metric("📈 Current Implied Earnings Move", f"{imp_earn_mv:.2f}%")
            if expected_price_change:
                st.metric("📉 Expected Price Change", f"±${expected_price_change:.2f}")  # Shows the expected move
            st.metric("📉 Average Historical Earnings Move", f"{abs_avg_earn_mv:.2f}%")
            st.metric("📅 Next Earnings Date", next_earn_date)

            # Format historical earnings moves as percentages
            df = pd.DataFrame(list(historical_moves.items()), columns=["Earnings Move", "Percentage"])
            df["Percentage"] = df["Percentage"].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")

            # Display table
            st.table(df)

