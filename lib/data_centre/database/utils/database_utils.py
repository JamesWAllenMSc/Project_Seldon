from contextlib import contextmanager
from mysql.connector import connect, Error
from lib.data_centre.database.config.database_logging_config import logger
from lib.data_centre.database.config.database_config import TABLE_SCHEMA
# Third-party imports
import pandas as pd

@contextmanager
def db_connection(access):
    """Creates and manages database connections automatically."""
    conn = None
    try:
        conn = connect(
            host=access['host'],
            user=access['user'],
            password=access['password'],
            database=access['database'],
            port=access['port']
        )
        yield conn.cursor()
        conn.commit()
    except Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()


def execute_query(access, query):
    """Executes a SQL query using the database connection."""
    with db_connection(access) as cursor:
        cursor.execute(query)
        logger.debug(f"Execution complete for query: {query}")


def retrieve_table(access, query):
    """Takes access credentials and query and returns table as list of tuples."""
    with db_connection(access) as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
        logger.debug(f"Execution complete for query: {query}")
        return table


def add_stock_price(global_price_df, exchange, year, access):
    """ Takes a dataframe of stock prices and adds them to the database
    --------------------------------------------------------------------------
    """
    # FORMAT STOCK PRICE DATA FOR UPLOAD TO SELDON_DB      
    global_prices_columns = global_price_df.columns.values # Get column names from stock price data
    columns = ', '.join(global_prices_columns) # Columns prepped 
    # stock_price = stock_price_df.replace({np.nan:'None'}) # Replace NaN values with None
    global_prices = str(global_price_df.values.tolist()) # Convert stock price data to list
    global_prices = global_prices.replace('[', '(').replace(']', ')') # Replace brackets with parentheses
    global_prices = global_prices[1:-1] # Remove first and last characters (brackets)
    
    # ADD STOCK PRICES TO SELDON_DB
    add_record_query = f'INSERT INTO prices_{exchange}_{year} ({columns}) VALUES {global_prices};'
    execute_query(access, add_record_query)
    logger.debug(f"Global prices added to seldon_db")



def reset_price_tables(access):
    """ Takes access credentials and resets all global_price tables in the database
    --------------------------------------------------------------------------
    """
    retrieve_enchange_codes_query = 'SELECT Code FROM global_exchanges'
    exchange_code_list = retrieve_table(access, retrieve_enchange_codes_query)
    exchange_code_list = [item[0] for item in exchange_code_list] # Convert list of tuples to list of strings

    for exchange_code in exchange_code_list:
        drop_prices_tables_query = f'DROP TABLE IF EXISTS global_prices_{exchange_code}'
        execute_query(access, drop_prices_tables_query)
        create_prices_table_query = f"""CREATE TABLE IF NOT EXISTS global_prices_{exchange_code} (
                                    Ticker_ID VARCHAR(255),
                                    Date DATE,
                                    Open DECIMAL(20,6),
                                    High DECIMAL(20,6),
                                    Low DECIMAL(20,6),
                                    Close DECIMAL(20,6),
                                    Adjusted_Close DECIMAL(20,6),
                                    Volume BIGINT
                                );"""
        execute_query(access, create_prices_table_query) 


def clear_all_tables(access: dict) -> None:
    """Clear all tables from the database.
    
    Args:
        access: Database connection configuration dictionary
        
    Returns:
        None
        
    Raises:
        mysql.connector.Error: If database operations fail
    """
    try:
        # Get list of all tables
        tables = retrieve_table(access, "SHOW TABLES;")
        
        if not tables:
            logger.info("No tables to drop")
            return
            
        # Extract table names and drop each table
        table_names = [table[0] for table in tables]
        for table in table_names:
            execute_query(access, f"DROP TABLE IF EXISTS {table};")
            logger.debug(f"Dropped table: {table}")
            
        logger.info(f"Successfully dropped {len(table_names)} tables")
        
    except Error as e:
        logger.error("Failed to clear tables", exc_info=True)
        raise


def clear_all_views(access: dict) -> None:
    """Clear all views in the database.
    
    Args:
        access: Database connection configuration dictionary
    """
    query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.VIEWS 
        WHERE TABLE_SCHEMA = DATABASE();
    """
    
    try:
        views = retrieve_table(access, query)
        if not views:
            logger.info("No views to clear")
            return
            
        view_names = [view[0] for view in views]
        for view in view_names:
            execute_query(access, f"DROP VIEW IF EXISTS {view};")
            logger.debug(f"Dropped view: {view}")
            
        logger.info(f"Successfully cleared {len(view_names)} views")
            
    except Error as e:
        logger.error("Failed to clear views", exc_info=True)
        raise