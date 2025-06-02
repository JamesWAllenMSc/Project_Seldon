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
- 📅 Daily price updates
- 🔍 Historical data retrieval

## Architecture

## Project Structure
```text
Project_Seldon/
├── config/
│   ├── connections/           # Connection configurations
│   │   ├── database.py       # Database credentials
│   │   └── api.py           # API keys and endpoints
│   └── settings/             # Global settings
│       ├── logging.py        # Logging configuration
│       └── paths.py         # System paths
├── lib/
│   └── data_centre/
│       └── database/
│           ├── scripts/      # Core processing scripts
│           │   ├── exchanges_update.py
│           │   ├── tickers_update.py
│           │   ├── populate_price_history.py
│           │   └── daily_price_update.py
│           └── utils/        # Utility functions
│               ├── database_utils.py
│               └── eodhd_utils.py
├── logs/                     # Application logs
├── tests/                    # Test suite
├── main.py                   # Entry point
└── README.md
```

### Database Schema

#### Global Exchanges
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

#### Price Tables
```sql
CREATE TABLE prices_{exchange}_{year} (
    Ticker_ID VARCHAR(255),
    Date DATE,
    Open DECIMAL(20,6),
    High DECIMAL(20,6),
    Low DECIMAL(20,6),
    Close DECIMAL(20,6),
    Adjusted_Close DECIMAL(20,6),
    Volume BIGINT
);
```

## Technical Details

### Recent Code Improvements
1. **API Integration**
   - 🔌 Added context managers for API requests
   - 🛠️ Implemented API endpoint dataclass
   - 🛡️ Enhanced error handling for API calls
   - 🔄 Added retry logic for failed requests

2. **Data Processing**
   - 🧹 Standardized DataFrame column orders
   - ✅ Added data validation checks
   - 🔄 Improved error recovery
   - 🛠️ Enhanced data transformation utilities

3. **Database Operations**
   - ⚡ Implemented connection pooling
   - 🔒 Added transaction management
   - 🚀 Enhanced query performance
   - 🛡️ Improved error handling

4. **Logging System**
   - 📝 Added structured logging
   - 🔄 Implemented log rotation
   - 🛡️ Enhanced error tracking
   - 🐛 Added debug logging

### New Features
1. **Daily Price Updates**
   - 📅 Automated daily data retrieval
   - 🔍 Intelligent update checking
   - 🧹 Gap detection and filling
   - ⚡ Performance optimization

2. **Historical Data**
   - 📊 Year-based table partitioning
   - 🗃️ Efficient data storage
   - 🔄 Historical gap filling
   - ✅ Data validation

3. **Exchange Management**
   - 🌍 Enhanced exchange filtering
   - 🇺🇸 Special handling for US markets
   - 💱 Currency conversion support
   - ⏰ Market hours tracking

## Updates Log

### May 2025
- ✅ Added daily price update automation
- ✅ Implemented API endpoint dataclass
- ✅ Enhanced error handling
- ✅ Improved data validation
- ✅ Added connection pooling
- ✅ Enhanced logging system
- ✅ Optimized database queries
- ✅ Added market hours tracking

### Future Plans
- 🔄 Add real-time price updates
- 🔍 Implement data analytics module
- 📊 Add visualization tools
- 🔐 Enhance security features
- 📱 Create API endpoints
- 🤖 Add automation tools

## Author
**James Allen**  
Creation Date: May 8, 2025  
Last Updated: May 12, 2025