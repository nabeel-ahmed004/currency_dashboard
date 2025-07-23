# Currency Exchange Dashboard

This is a real-time currency exchange dashboard built using Streamlit and Python. It fetches live currency exchange rates using ExchangeRate API, logs them to Google Sheets, and visualizes currency trends using Plotly.

## Tools & Technologies
- **Python**
- **Streamlit**
- **ExchangeRate API**
- **Google Sheets API** via `gspread`
- **Plotly** for trend visualization

## Setup Instructions

1. Clone this project or download the `currency_dashboard.py` file.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Place your `credentials.json` file (Google service account) in the root folder.
4. Run the dashboard:
   ```bash
   streamlit run currency_dashboard.py
   ```

## Features

- Select a base currency dynamically.
- Choose 3–15 target currencies to compare.
- View live exchange rates using ExchangeRate API.
- Log each exchange check to a Google Sheet.
- Display trend charts for historical exchange rates.

## Author
This project was built during an internship with **Redline Intelligence**.
