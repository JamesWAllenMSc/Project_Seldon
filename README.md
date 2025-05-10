# Project Seldon

> "The larger the mass of humanity being dealt with, the greater the accuracy of psychohistorical predictions."  
> *- Second Foundation Theorem*

## Overview
A financial data management system that retrieves and processes stock market data from EODHD API.

## Project Structure
```
Project_Seldon/
├── lib/
│   └── data_centre/
│       └── database/
│           ├── config/
│           │   ├── database_config.py
│           │   ├── database_access_config.py
│           │   ├── database_logging_config.py
│           │   └── eodhd_access_config.py
│           ├── scripts/
│           │   ├── __init__.py
│           │   ├── exchanges_update.py
│           │   └── tickers_update.py
│           └── utils/
│               ├── database_utils.py
│               └── eodhd_utils.py
├── logs/
│   └── database_logs/
├── main.py
└── README.md
```

## Components

### Database Configuration
- Centralized configuration management
- Environment-based settings
- Logging configuration with file and console handlers
- API access management

### Database Utilities
- Connection management using context managers
- Query execution helpers
- Table operations
- Error handling and logging

### Data Scripts
#### Exchange Updates
- Retrieves global exchange data from EODHD
- Maintains exchange database
- Validates data structure
- Tracks changes and updates

#### Ticker Updates
- Fetches ticker data for each exchange
- Updates global ticker database
- Handles missing data
- Validates data structure

### API Integration
- EODHD API client implementation
- Data validation and transformation
- Error handling and retry logic

## Recent Updates

### Code Improvements
1. Implemented context managers for database connections
2. Added comprehensive logging system
3. Improved error handling throughout
4. Added type hints for better code documentation
5. Reorganized imports and module structure
6. Implemented data validation checks
7. Added helper functions for common operations

### Database Structure
1. Created global exchanges table
2. Implemented global tickers table
3. Added primary keys and constraints
4. Optimized table structure

### Data Processing
1. Added exchange filtering
2. Implemented ticker validation
3. Added data transformation utilities
4. Improved error recovery

## Features
- Automatic database initialization
- Real-time exchange data updates
- Ticker synchronization
- Data validation and cleaning
- Error logging and monitoring
- Modular design for easy expansion

## Logging
- Comprehensive logging system
- File and console output
- Different log levels for debugging
- Structured log format
- Automatic log rotation

## Database Schema

### Global Exchanges
```sql
CREATE TABLE global_exchanges (
    Name VARCHAR(255),
    Code VARCHAR(255),
    OperatingMIC VARCHAR(255),
    Country VARCHAR(255),
    Currency VARCHAR(255),
    CountryISO2 VARCHAR(255),
    CountryISO3 VARCHAR(255),
    Source VARCHAR(255),
    Date_Updated DATETIME,
    PRIMARY KEY (Code)
);
```

### Global Tickers
```sql
CREATE TABLE global_tickers (
    Ticker_ID VARCHAR(255),
    Code VARCHAR(255),
    Name VARCHAR(255),
    Country VARCHAR(255),
    Exchange VARCHAR(255),
    Currency VARCHAR(255),
    Type VARCHAR(255),
    Isin VARCHAR(255),
    Source VARCHAR(255),
    Date_Updated DATETIME,
    PRIMARY KEY (Ticker_ID)
);
```

## Author
**James Allen**  
Twitter: [@JamesAllenMSc](https://twitter.com/JamesAllenMSc)  
Creation Date: May 8, 2025