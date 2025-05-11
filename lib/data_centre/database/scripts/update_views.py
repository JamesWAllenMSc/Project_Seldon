# Standard library imports

# Third-party imports
import pandas as pd

# Local application imports
from utils import database_utils
from lib.data_centre.database.config.database_logging_config import logger
from lib.data_centre.database.config.database_config import TABLE_SCHEMA


def update_close_price_view(access):
    """ This function retrieves the current views in the seldon_db_dev database
    and compares them to the views in the views folder. If any views are missing
    in the database, they are created.
    """
    try:
        # Get list of exchanges from the database
        exchanges_query = "SELECT Code FROM global_exchanges;"
        exchanges = database_utils.retrieve_table(access, exchanges_query)
        exchanges = pd.DataFrame(exchanges, columns=['Code'])
        exchanges = exchanges['Code'].to_list()
        for exchange in exchanges:
            
            # Get table list for each exchange
            table_list_query = f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{TABLE_SCHEMA}' AND TABLE_NAME LIKE '%{exchange}_%';"
            table_list = database_utils.retrieve_table(access, table_list_query)
            table_list = pd.DataFrame(table_list, columns=['TABLE_NAME'])
            table_list = table_list['TABLE_NAME'].to_list()
            print(table_list)
            full_query = f"""CREATE VIEW IF NOT EXISTS {exchange}_close_price AS"""
            for table in table_list:
                table_element = f""" SELECT Ticker_ID, Date, Close from {table} UNION ALL"""
                full_query = full_query + table_element
            full_query = full_query[:-10] + ";"
            # Execute the query to create the view
            database_utils.execute_query(access, full_query)
            logger.info(f"View {exchange}_close_price created successfully.")
    except Exception as e:
        logger.error(f"Error creating view {exchange}_close_price: {e}")

def update_all_views(access):
    update_close_price_view(access)
