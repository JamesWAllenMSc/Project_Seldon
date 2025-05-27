# Standard library imports

# Third-party imports
import pandas as pd

# Local application imports
from lib.data_centre.database.utils import database_utils
from config.connections.database_access import TABLE_SCHEMA
from config.settings.logging import logger_factory

logger = logger_factory.get_logger('database', module_name=__name__)


def create_close_price_view(access: dict, exchange: str, table_list: list) -> bool:
    """Creates a view combining close prices for all tables of an exchange."""
    try:
        view_name = f"{exchange}_close_price"
        query_parts = [f"CREATE VIEW IF NOT EXISTS {view_name} AS"]
        
        # Build UNION ALL query for all tables
        select_queries = [
            f"SELECT Ticker_ID, Date, Close from {table}"
            for table in table_list
        ]
        query_parts.append(" UNION ALL ".join(select_queries))
        
        # Execute combined query
        full_query = " ".join(query_parts) + ";"
        database_utils.execute_query(access, full_query)
        logger.debug(f"View {view_name} created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create view {view_name}: {e}")
        return False

def update_close_price_view(access: dict) -> None:
    """Updates all exchange close price views in the database."""
    try:
        # Get list of exchanges
        exchanges = pd.DataFrame(
            database_utils.retrieve_table(access, "SELECT Exchange FROM global_exchanges;"),
            columns=['Exchange']
        )['Exchange'].tolist()
        
        exchanges_stats = {
            'checked': 0,
            'created': 0,
            'missed': []
        }
        
        # Process each exchange
        for exchange in exchanges:
            exchanges_stats['checked'] += 1
            
            # Get tables for this exchange
            table_list = pd.DataFrame(
                database_utils.retrieve_table(
                    access,
                    f"""SELECT TABLE_NAME 
                       FROM INFORMATION_SCHEMA.TABLES 
                       WHERE TABLE_SCHEMA = '{TABLE_SCHEMA}' 
                       AND TABLE_NAME LIKE '%{exchange}_%';"""
                ),
                columns=['TABLE_NAME']
            )['TABLE_NAME'].tolist()
            
            if not table_list:
                logger.debug(f"No tables found for exchange {exchange}")
                exchanges_stats['missed'].append(exchange)
                continue
                
            if create_close_price_view(access, exchange, table_list):
                exchanges_stats['created'] += 1
        
        logger.info(
            f"Checked {exchanges_stats['checked']} exchanges, "
            f"created {exchanges_stats['created']} views. "
            f"Unable to create views for exchanges: {exchanges_stats['missed']}"
        )
        
    except Exception as e:
        logger.error(f"Failed to update close price views: {e}")

def update_all_views(access: dict) -> None:
    """Updates all database views."""
    update_close_price_view(access)