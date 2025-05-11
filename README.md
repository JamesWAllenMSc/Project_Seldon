# Project Seldon

> "The larger the mass of humanity being dealt with, the greater the accuracy of psychohistorical predictions."  
> *- Second Foundation Theorem*

## Overview
Project Seldon is a robust financial data management system that retrieves, processes, and stores stock market data from the EODHD API. It features automated data synchronization, comprehensive error handling, and modular design for scalability.

## Key Features
- 📊 Real-time exchange data updates
- 🔄 Automated ticker synchronization
- 🧹 Data validation and cleaning
- 📝 Comprehensive logging system
- 🔌 Modular plugin architecture
- 🛡️ Robust error handling

## Architecture

### Core Components
```
Project_Seldon/
├── lib/
│   └── data_centre/
│       └── database/
│           ├── config/      # Configuration management
│           ├── scripts/     # Data processing scripts
│           └── utils/       # Utility functions
├── logs/                    # Application logs
└── main.py                  # Entry point
```

### Database Schema

#### Global Exchanges
Stores information about stock exchanges worldwide.
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

#### Global Tickers
Maintains comprehensive ticker data across all exchanges.
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

## Technical Details

### Data Processing Pipeline
1. **Exchange Updates**
   - Retrieves global exchange data
   - Validates data structure
   - Updates database records
   - Tracks changes

2. **Ticker Management**
   - Fetches ticker data per exchange
   - Handles missing data
   - Validates data integrity
   - Updates global ticker database

3. **Price History**
   - Retrieves historical price data
   - Processes data by year
   - Maintains separate price tables
   - Handles data gaps

### Logging System
- Structured log format
- Multiple output handlers
- Configurable log levels
- Automatic rotation
- Error tracking

### Error Handling
- Comprehensive exception management
- Automatic retry logic
- Data validation checks
- Detailed error logging
- Recovery procedures

## Recent Updates

### Code Improvements
- ✅ Implemented database connection context managers
- ✅ Added comprehensive logging system
- ✅ Enhanced error handling
- ✅ Added type hints
- ✅ Reorganized module structure
- ✅ Implemented data validation
- ✅ Added utility functions

### Data Processing
- ✅ Added exchange filtering
- ✅ Implemented ticker validation
- ✅ Enhanced data transformation
- ✅ Improved error recovery
- ✅ Optimized database operations

## Author
**James Allen**  
Twitter: [@JamesAllenMSc](https://twitter.com/JamesAllenMSc)  
Creation Date: May 8, 2025