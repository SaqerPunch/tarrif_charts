from fredapi import Fred
import pandas as pd
import numpy as np
from datetime import datetime
import wbdata as wb
import yfinance as yf
import requests


TRADE_DEFICIT = "NETEXP"

#CPI
fred = Fred(api_key= 'a188bdb98c824eb9c21e9e236b5e05b4')
# Get the data as a Series
series = fred.get_series(TRADE_DEFICIT, observation_start='2015-01-01', observation_end='2025-01-01')

# Convert it to a DataFrame
trade_data = series.reset_index()
trade_data.columns = ['Date', 'Trade Balance']  # Rename columns if needed

# Optional: Save to CSV
print(trade_data)
trade_data.to_csv('data-sets/us_trade_data.csv', index=False)


######
# Set the countries you're interested in
countries = ['USA', 'CHN', 'DEU', 'JPN']

# Set the indicator for inflation (consumer prices)
indicator = {'FP.CPI.TOTL.ZG': 'Inflation'}

# Set the date range from 2013 to 2025
start_date = datetime(2013, 1, 1)
end_date = datetime(2025, 1, 1)

# Get data from the World Bank
world_inflation = wb.get_dataframe(indicator, country=countries, date=(start_date, end_date))

# Reset the index to have the year as a column
world_inflation.reset_index(inplace=True)

world_inflation = world_inflation.pivot(index='date', columns='country', values='Inflation')

# Display the DataFrame
print(world_inflation)
world_inflation.to_csv('data-sets/world_inflation_data.csv', index=False)



####

import pandas as pd

# Load each CSV file
eur = pd.read_csv("historical-data/USD_EUR.csv", usecols=["Date", "Price"])
jpy = pd.read_csv("historical-data/USD_JPY.csv", usecols=["Date", "Price"])
cny = pd.read_csv("historical-data/USD_CNY.csv", usecols=["Date", "Price"])

for fx_data in [eur, jpy, cny]:
    fx_data["Date"] = pd.to_datetime(fx_data["Date"], format="%m/%d/%Y")
    fx_data.sort_values("Date", inplace=True)

# Rename price columns before merging
eur.rename(columns={"Price": "USD_EUR"}, inplace=True)
jpy.rename(columns={"Price": "USD_JPY"}, inplace=True)
cny.rename(columns={"Price": "USD_CNY"}, inplace=True)

# Calculate price change
eur["USD_EUR_Change"] = eur["USD_EUR"].diff()
jpy["USD_JPY_Change"] = jpy["USD_JPY"].diff()
cny["USD_CNY_Change"] = cny["USD_CNY"].diff()

# Merge everything on Date
fx_data = eur.merge(jpy, on="Date", how="outer").merge(cny, on="Date", how="outer")

# Sort by date descending
fx_data.sort_values("Date", ascending=False, inplace=True)

# Optional: Save to CSV
fx_data.to_csv("data-sets/fx_data.csv", index=False)


#####
CPI_SERIES = 'CPIAUCSL'         # CPI (Consumer Price Index)
WAGE_SERIES = 'CES0500000003'   # Average Hourly Earnings, Total Private Employees

# Get monthly data from FRED
cpi = fred.get_series(CPI_SERIES).to_frame(name='CPI')
wages = fred.get_series(WAGE_SERIES).to_frame(name='Wages')

# Combine into one DataFrame
df = pd.concat([cpi, wages], axis=1).dropna()

# Ensure monthly frequency
df = df.resample('M').last().dropna()

# Compute Year-over-Year % change
df['CPI_YoY'] = df['CPI'].pct_change(12) * 100
df['Wage_YoY'] = df['Wages'].pct_change(12) * 100

# Compute Real Wage Growth
df['Real_Wage_Growth'] = df['Wage_YoY'] - df['CPI_YoY']

# Export to CSV
df.to_csv('data-sets/monthly_inflation_vs_wage_growth.csv')

# Preview result
print(df.tail())
