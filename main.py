import streamlit as st
import requests
from dataclasses import dataclass
import numpy as np
import pandas as pd
from datetime import datetime

@dataclass
class StockData:
    symbol: str
    daily_prices: list
    dates: list

    def calculate_daily_returns(self):
        returns = []
        for i in range(1, len(self.daily_prices)):
            today = self.daily_prices[i]
            yesterday = self.daily_prices[i - 1]
            daily_return = (today - yesterday) / yesterday
            returns.append(daily_return)
        return returns

    def calculate_sharpe_ratio(self, risk_free_rate=0.0):
        returns = self.calculate_daily_returns()
        excess_returns = [r - risk_free_rate for r in returns]
        return np.mean(excess_returns) / np.std(excess_returns)

def fetch_stock_data(symbol, api_key):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()

    time_series = data.get("Time Series (Daily)", {})
    dates = list(time_series.keys())
    daily_prices = [float(time_series[day]["4. close"]) for day in time_series]
    return daily_prices, dates

def filter_current_year_data(dates, values):
    current_year = datetime.now().year
    filtered_dates = []
    filtered_values = []
    for date, value in zip(dates, values):
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        if date_obj.year == current_year:
            filtered_dates.append(date_obj)
            filtered_values.append(value)
    return filtered_dates, filtered_values

def main():
    st.title('Stock Data Analysis')

    symbol = st.sidebar.text_input("Enter Stock Symbol", value='ICLN')

    if symbol:
        api_key = '7N2BGL250AWUW9LU'
        daily_prices, dates = fetch_stock_data(symbol, api_key)
        stock_data = StockData(symbol, daily_prices, dates)

        daily_returns = stock_data.calculate_daily_returns()
        sharpe_ratio = stock_data.calculate_sharpe_ratio()

        # Filter data for the current year
        filtered_dates, filtered_prices = filter_current_year_data(dates, daily_prices)
        _, filtered_return_dates = filter_current_year_data(dates[1:], dates[1:]) 
        _, filtered_returns = filter_current_year_data(dates[1:], daily_returns)  

        st.write(f"Sharpe Ratio for {symbol}: {sharpe_ratio}")

        df_prices = pd.DataFrame({'Price': filtered_prices}, index=pd.to_datetime(filtered_dates))
        st.line_chart(df_prices)

        if len(filtered_returns) == len(filtered_return_dates):
            df_returns = pd.DataFrame({'Returns': filtered_returns}, index=pd.to_datetime(filtered_return_dates))
            st.line_chart(df_returns)
        else:
            st.error("Error: Mismatch in dates and returns data lengths.")

if __name__ == "__main__":
    main()
    