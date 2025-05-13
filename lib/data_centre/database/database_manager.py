""" Runs the database manager for the data center.
    Includes the following:
        - Daily updates of price and stock data
        - Monthly updates of global exchanges and new tickers
"""

# Standard library imports
from pathlib import Path
import time

# Local application imports
from config.database_config import PATHS
from lib.data_centre.database.scripts import daily_price_update
from lib.data_centre.database.config.database_logging_config import logger
from config.database_access_config import DB_CONFIG

# Third party imports
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from lib.data_centre.database.scripts import (exchanges_update, 
                                              tickers_update, 
                                              update_all_views)


# Set sys.path modification
project_root = PATHS['DATABASE']


def main():
    """ Main function to schedule tasks using APScheduler """
    logger.info("Starting Seldon database management scripts...")

    # Create a BackgroundScheduler
    scheduler = BackgroundScheduler()

    # Schedule `run_daily_updates` at 1:00 AM and 1:00 PM every day
    scheduler.add_job(daily_price_update, CronTrigger(hour=1, minute=0))
    scheduler.add_job(daily_price_update, CronTrigger(hour=13, minute=0))

    # Schedule a task to run every Sunday at 2:00 AM
    scheduler.add_job(exchanges_update(DB_CONFIG), CronTrigger(day_of_week='sun', hour=2, minute=0))

    # Schedule a task to run every Sunday at 2:15 AM
    scheduler.add_job(tickers_update(), CronTrigger(day_of_week='sun', hour=2, minute=15))

    # Schedule a task to run every Sunday at 2:30 AM
    scheduler.add_job(update_all_views(DB_CONFIG), CronTrigger(day_of_week='sun', hour=2, minute=30))

    # Start the scheduler
    scheduler.start()

    while True:
        time.sleep(1)
   

if __name__ == "__main__":
    main()




