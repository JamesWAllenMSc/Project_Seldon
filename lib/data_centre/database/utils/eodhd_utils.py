""" Utilities and function to interact with EODHD API
"""

# Set sys.path modification
from config.database_config import PATHS
project_root = PATHS['DATABASE']

# Standard library imports
import datetime

# Third-party imports
import pandas as pd
import requests

# Local application imports
# from config.eodhd_access_config import EODHD_CONFIG['api_key'] as eodhd_api
from lib.data_centre.database.config.database_logging_config import logger

""""
import logging


# Standard library imports
import sys
from pathlib import Path

# Third-party imports
from mysql.connector import connect, Error

from utils import database_utils
from scripts import exchanges_update
from lib.data_centre.database.scripts import exchanges_update
"""

def retrieve_tickers(eodhd_api, exchange):
    """ Takes api credentials for eodhd.com and a target exchange and returns a pandas dataframe containing 
    all tickers from the target exchange
    """
    url = f'https://eodhd.com/api/exchange-symbol-list/{exchange}?api_token={eodhd_api}&fmt=json'
    try:
        ticker_data = requests.get(url).json()

        # Check if response is empty or invalid
        if not ticker_data or not isinstance(ticker_data, list):
            return None

        ticker_data = pd.DataFrame(ticker_data)
        ticker_data['Source'] = f'EoDHD.com - Exchange {exchange}' # Adds Source column
        ticker_data['Date_Updated'] = datetime.datetime.now() # Adds timestamp
        id = ticker_data['Code']+f'_{exchange}'
        ticker_data['Ticker_ID'] = id
        ticker_columns = ['Ticker_ID', 'Code', 'Name', 'Country', 'Exchange',
                        'Currency', 'Type', 'Isin', 'Source',
                        'Date_Updated']
        ticker_data = ticker_data[ticker_columns]
        return ticker_data
    except Exception as e:
        logger.error(f'Exchange: {exchange} -  {e}', exc_info=True)
    
          

def retrieve_exchanges(eodhd_api):
    """ Takes api credentials for eodhd.com and returns full list of available exchanges
    """
    try:
        url = f'https://eodhd.com/api/exchanges-list/?api_token={eodhd_api}&fmt=json'
        exc_data = requests.get(url).json()
        exc_data = pd.DataFrame(exc_data)
        # exc_data = exc_data[exc_data['Name'] != 'USA Stocks'] # Removing grouped US stocks
        exc_data['Source'] = 'EoDHD.com' # Adds Source column
        exc_data['Date_Updated'] = datetime.datetime.now() # Adds timestampus_stocks = pd.DataFrame.from_dict({
        # Add in individual US exchanges
        us_stocks = pd.DataFrame.from_dict({
            'Name':['New York Stock Exchange', 'NASDAQ'],
            'Code':['NYSE', 'NASDAQ'],
            'OperatingMIC':['XNYS', 'XNAS'],
            'Country':['US', 'US'],
            'Currency':['USD', 'USD'],
            'CountryISO2':['US', 'US'],
            'CountryISO3':['USA', 'USA'],
            'Source':['Manual_Input', 'Manual_Input'],
            'Date_Updated':[datetime.datetime.now(), datetime.datetime.now()]
        })
        exc_data = pd.concat([exc_data, us_stocks], ignore_index=True)
        return(exc_data)
    except Exception as e:
        logger.error(e, exc_info=True)
    


def retrieve_historical_price(exchange, ticker, date_to, eodhd_api):
    """ Takes api credentials for eodhd.com, a ticker and date range and returns a pandas dataframe containing 
    all historical prices for the target ticker
    """
    eod_ticker = f'{ticker}.{exchange}' # EoDHD.com ticker format
    url = f'https://eodhd.com/api/eod/{eod_ticker}?api_token={eodhd_api}&from={'1900-01-01'}&to={date_to}&fmt=json'
    try:
        price_data = requests.get(url).json()
        price_data = pd.DataFrame(price_data)
        id = f'{eod_ticker}'.replace('.', '_')  # Replace '.' with '_' to create a valid Ticker_ID
        price_data['Ticker_ID'] = id
        price_data_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adjusted_Close',
                        'Volume', 'Ticker_ID'] 
        price_data.columns = price_data_columns[:len(price_data.columns)]
        price_data_columns_order = ['Ticker_ID', 'Date', 'Open', 'High', 'Low', 'Close', 'Adjusted_Close',
                        'Volume'] # Rearranging columns
        price_data = price_data[price_data_columns_order] # Specyfying column order to support db upload
        return price_data
    except Exception as e:
        logger.error(f'Updating historical price data -Ticker: {ticker} -  {e}')



def retrieve_daily_price(exchange, eodhd_api):
    """ Takes exchenge and api credentials for eodhd.com and returns a pandas dataframe containing
    all daily prices for the target exchange
    """
    url = f'https://eodhd.com/api/eod-bulk-last-day/{exchange}?api_token={eodhd_api}&fmt=json'
    try:
        price_data = requests.get(url).json()
        price_data = pd.DataFrame(price_data)
        id = price_data['code']+f'_{exchange}'  # Create Ticker_ID
        price_data['Ticker_ID'] = id
        price_data = price_data.drop(columns=['code', 'exchange_short_name'])
        price_data_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adjusted_Close',
                        'Volume', 'Ticker_ID'] 
        price_data.columns = price_data_columns[:len(price_data.columns)]
        price_data_columns_order = ['Ticker_ID', 'Date', 'Open', 'High', 'Low', 'Close', 'Adjusted_Close',
                        'Volume'] # Rearranging columns
        price_data = price_data[price_data_columns_order] # Specyfying column order to support db upload
        
        return price_data
    except Exception as e:
        logger.error(f'Updating daily price data -Exchange: {exchange}')