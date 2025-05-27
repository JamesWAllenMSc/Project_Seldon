"""EODHD API Integration Module

This module provides utilities for interacting with the EODHD API,
handling data retrieval and transformation for exchanges, tickers, and price data.
"""

from typing import Optional, Dict, Any
import datetime
from dataclasses import dataclass

import pandas as pd
import requests

from config.settings.logging import logger_factory

logger = logger_factory.get_logger('database', module_name=__name__)

# Constants
PRICE_COLUMNS_SORTED = [
    'Ticker_ID', 'Ticker', 'EoDHD_Exchange', 'Date', 'Open', 'High', 'Low', 
    'Close', 'Adjusted_Close', 'Volume'
]

PRICE_COLUMNS = [
    'Date', 'Open', 'High', 'Low', 'Close', 'Adjusted_Close', 
    'Volume', 'Ticker_ID'
]

US_EXCHANGES = {
    'NYSE': {
        'Name': 'New York Stock Exchange',
        'OperatingMIC': 'XNYS',
        'Country': 'US',
        'Currency': 'USD',
        'CountryISO2': 'US',
        'CountryISO3': 'USA',
    },
    'NASDAQ': {
        'Name': 'NASDAQ',
        'OperatingMIC': 'XNAS',
        'Country': 'US',
        'Currency': 'USD',
        'CountryISO2': 'US',
        'CountryISO3': 'USA',
    },
    'PINK': {
        'Name': 'OTC Markets Group',
        'OperatingMIC': 'OTCM',
        'Country': 'US',
        'Currency': 'USD',
        'CountryISO2': 'US',
        'CountryISO3': 'USA',
    },
    'NMFQS': {
        'Name': 'Money Market Obligations Trust - Federated Hermes California Municipal Cash Trust',
        'OperatingMIC': 'NMFQS',
        'Country': 'US',
        'Currency': 'USD',
        'CountryISO2': 'US',
        'CountryISO3': 'USA',
    },
    'NYSE_ARCA': {
        'Name': 'NYSE Arca',
        'OperatingMIC': 'XNYS',
        'Country': 'US',
        'Currency': 'USD',
        'CountryISO2': 'US',
        'CountryISO3': 'USA',
    },
    'NYSE_MKT': {
        'Name': 'NYSE American (Small Cap Stocks)',
        'OperatingMIC': 'XASE',
        'Country': 'US',
        'Currency': 'USD',
        'CountryISO2': 'US',
        'CountryISO3': 'USA',
    }
}


@dataclass
class APIEndpoints:
    """EODHD API endpoint configurations."""
    BASE_URL = "https://eodhd.com/api"
    EXCHANGES = f"{BASE_URL}/exchanges-list"
    TICKERS = f"{BASE_URL}/exchange-symbol-list"
    HISTORICAL = f"{BASE_URL}/eod"
    DAILY = f"{BASE_URL}/eod-bulk-last-day"


def _make_api_request(url: str) -> Optional[Dict[str, Any]]:
    """Make API request with error handling."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}", exc_info=True)
        return None


def retrieve_tickers(api_key: str, exchange: str) -> Optional[pd.DataFrame]:
    """Retrieve ticker data for a specific exchange.
    
    Args:
        api_key: EODHD API key
        exchange: Exchange code
    
    Returns:
        DataFrame containing ticker data or None if request fails
    """
    url = f"{APIEndpoints.TICKERS}/{exchange}?api_token={api_key}&fmt=json"
    data = _make_api_request(url)
    if not data or not isinstance(data, list):
        return None
        
    try:
        df = pd.DataFrame(data)
        df.rename(columns={'Code': 'Ticker'}, inplace=True)
        df['Source'] = f'EoDHD.com - Exchange {exchange}'
        df['Date_Updated'] = datetime.datetime.now()
        df['Ticker_ID'] = df['Ticker'] + f'_{exchange}'
        df['EoDHD_Exchange']=df['Exchange'].apply(lambda x: 'US' if x in list(US_EXCHANGES.keys()) else x)

        
        return df[['Ticker_ID', 'Ticker', 'Name', 'Country', 'Exchange', 'EoDHD_Exchange',
                  'Currency', 'Type', 'Isin', 'Source', 'Date_Updated']]
    except Exception as e:
        logger.error(f"Failed to process ticker data for {exchange}: {e}")
        return None


def retrieve_exchanges(api_key: str) -> Optional[pd.DataFrame]:
    """Retrieve all available exchanges with US exchange handling.
    
    Args:
        api_key: EODHD API key
    
    Returns:
        DataFrame containing exchange data or None if request fails
    """
    url = f"{APIEndpoints.EXCHANGES}/?api_token={api_key}&fmt=json"
    data = _make_api_request(url)
    
    
    if not data:
        return None
        
    try:
        # Process EODHD exchanges
        df = pd.DataFrame(data)
        df['Source'] = 'EoDHD.com'
        df['Date_Updated'] = datetime.datetime.now()
        
        # Add US exchanges
        us_exchanges = pd.DataFrame([
            {**exchange_data, 'Code': code, 'Source': 'Manual_Input', 
             'Date_Updated': datetime.datetime.now()}
            for code, exchange_data in US_EXCHANGES.items()
        ])
        
        return pd.concat([df, us_exchanges], ignore_index=True)
    except Exception as e:
        logger.error(f"Failed to process exchange data: {e}", exc_info=True)
        return None


def retrieve_historical_price(exchange, ticker, date_to, eodhd_api):
    """ Takes api credentials for eodhd.com, a ticker and date range and returns a pandas dataframe containing 
    all historical prices for the target ticker
    """
    eod_ticker = f'{ticker}.{exchange}' # EoDHD.com ticker format
    url = f'https://eodhd.com/api/eod/{eod_ticker}?api_token={eodhd_api}&from={'1900-01-01'}&to={date_to}&fmt=json'
    try:
        price_data = requests.get(url).json()
        price_data = pd.DataFrame(price_data)
        if price_data.empty:
            logger.debug(f"No data returned for Ticker: {ticker} on Exchange: {exchange}")
            return None
        price_data['Ticker_ID'] = None
        price_data.columns = PRICE_COLUMNS
                     
        return price_data
    except Exception as e:
        logger.error(f'Updating historical price data -Ticker: {ticker} -  {e}')


def retrieve_daily_price(eodhd_exchange: str, exchange: str, api_key: str) -> Optional[pd.DataFrame]:
    """Retrieve latest daily prices for all tickers in an exchange.
    
    Args:
        exchange: Exchange code
        api_key: EODHD API key
        
    Returns:
        DataFrame containing daily price data or None if request fails
    """
    url = f"{APIEndpoints.DAILY}/{eodhd_exchange}?api_token={api_key}&fmt=json"
    
    # Make API request using existing helper
    data = _make_api_request(url)
    if not data:
        logger.warning(f"No daily price data retrieved for {exchange} using EoDHD code {eodhd_exchange}")
        return None
        
    try:
        # Convert to DataFrame and process
        df = pd.DataFrame(data)
                
        # Create Ticker_ID and clean columns
        df['Ticker_ID'] = df['code'] + f'_{exchange}'
        df.columns = PRICE_COLUMNS
        df = df[PRICE_COLUMNS_SORTED]  # Specifying column order to support DB upload
        return df
        
    except Exception as e:
        logger.error(f"Failed to process daily prices for {exchange} retrieved using {eodhd_exchange}: {e}", exc_info=True)
        return None
    
