import streamlit as st
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- Config ---
SHEET_NAME = "Currency_Exchange_Log"
CREDENTIALS_FILE = "credentials.json"
API_KEY = "ab63afcaf73a491633b5391d"  # Replace with your actual key if needed

# --- Page Setup ---
st.set_page_config(page_title="Currency Exchange Dashboard", layout="wide")
st.title("Currency Exchange Dashboard")

# --- Fetch Supported Currencies ---
@st.cache_data
def get_supported_currencies():
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
    try:
        res = requests.get(url)
        data = res.json()
        if data.get("result") == "success":
            return list(data["conversion_rates"].keys())
        else:
            st.error("⚠️ Failed to fetch currency list from API.")
            st.json(data)
            return []
    except Exception as e:
        st.error(f"API error fetching currency codes: {e}")
        return []

available_currencies = get_supported_currencies()

# --- UI: Dropdowns ---
if available_currencies:
    base_currency = st.selectbox(
        "Choose base currency:",
        available_currencies,
        index=available_currencies.index("USD") if "USD" in available_currencies else 0
    )

    target_options = [c for c in available_currencies if c != base_currency]
    preferred = ["PKR", "EUR", "GBP", "INR", "JPY"]
    default_currencies = [c for c in preferred if c in target_options]

    target_currencies = st.multiselect(
        "Select currencies to display against base:",
        options=target_options,
        default=default_currencies[:10],
        max_selections=15
    )

    # --- Fetch Live Rates ---
    def get_exchange_rates(base):
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base}"
        try:
            res = requests.get(url)
            res.raise_for_status()
            data = res.json()

            if data.get("result") != "success":
                st.error("⚠️ API returned an error.")
                st.json(data)
                return {}

            return data["conversion_rates"]
        except Exception as e:
            st.error(f"❌ Failed to fetch exchange rates: {e}")
            return {}

    # --- Google Sheets Auth ---
    @st.cache_resource
    def connect_gsheet():
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        return sheet

    # --- Log to Sheet ---
    def log_to_sheet(sheet, base, targets, rates):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insert headers if empty
        if sheet.row_count == 0 or sheet.row_values(1) != ["Timestamp", "Base", "Currency", "Rate"]:
            sheet.insert_row(["Timestamp", "Base", "Currency", "Rate"], 1)

        for curr in targets:
            rate = rates.get(curr)
            if rate:
                row = [timestamp, base, curr, rate]
                sheet.append_row(row)

    # --- Plot Trend ---
    def plot_currency_trend(df, currency):
        df_filtered = df[df["Currency"] == currency]
        fig = px.line(df_filtered, x="Timestamp", y="Rate", title=f"{currency} Trend vs {base_currency}")
        st.plotly_chart(fig, use_container_width=True)

    # --- MAIN ---
    if target_currencies:
        rates = get_exchange_rates(base_currency)
        if rates:
            st.subheader(f"Live Exchange Rates (Base: {base_currency})")
            for curr in target_currencies:
                rate = rates.get(curr)
                if rate and rate > 0:
                    st.markdown(f"**1 {base_currency} = {rate:.2f} {curr}**")
                else:
                    st.warning(f"⚠️ No valid rate for {curr}")

            # Log to Sheet
            try:
                sheet = connect_gsheet()
                log_to_sheet(sheet, base_currency, target_currencies, rates)
            except Exception as e:
                st.error(f"Failed to log to Google Sheet: {e}")

            # Load & plot trends
            try:
                records = sheet.get_all_records()
                if records:
                    df_log = pd.DataFrame(records)
                    expected_cols = {"Timestamp", "Base", "Currency", "Rate"}
                    if expected_cols.issubset(df_log.columns):
                        df_log["Timestamp"] = pd.to_datetime(df_log["Timestamp"])
                        for curr in target_currencies:
                            plot_currency_trend(df_log[df_log["Base"] == base_currency], curr)
                    else:
                        st.warning("⚠️ Missing required columns in sheet.")
                else:
                    st.info("📝 No historical data logged yet.")
            except Exception as e:
                st.warning(f"📉 Could not load trend data: {e}")
        else:
            st.error("Failed to fetch exchange rates.")
    else:
        st.info("Please select at least one currency to display.")
else:
    st.error("⚠️ No currencies available. Check API key or internet.")
