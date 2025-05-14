""" Runs the database manager for the data center.
    Includes the following:
        - Daily updates of price and stock data
        - Monthly updates of global exchanges and new tickers
"""

# Standard library imports
from pathlib import Path
import time

# Set sys.path modification
from lib.data_centre.database.config.database_config import PATHS
project_root = PATHS['DATABASE']

# Local application imports
from lib.data_centre.database.scripts import daily_price_update
from lib.data_centre.database.config.database_logging_config import logger
from lib.data_centre.database.config.database_access_config import DB_CONFIG

# Third party imports
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from lib.data_centre.database.scripts import (exchanges_update, 
                                              tickers_update, 
                                              update_all_views)


def main():
    """ Main function to schedule tasks using APScheduler """
    logger.info("Starting Seldon database management scripts...")

    # Create a BackgroundScheduler
    scheduler = BackgroundScheduler()

    # Schedule `run_daily_updates` at 1:00 AM and 1:00 PM every day
    scheduler.add_job(daily_price_update, CronTrigger(hour=1, minute=0))
    scheduler.add_job(daily_price_update, CronTrigger(hour=13, minute=0))

    # Schedule weekly tasks - Note: Don't call the functions, just pass them
    scheduler.add_job(
        lambda: exchanges_update(DB_CONFIG), 
        CronTrigger(day_of_week='sun', hour=2, minute=0)
    )

    scheduler.add_job(
        tickers_update, 
        CronTrigger(day_of_week='sun', hour=2, minute=15)
    )

    scheduler.add_job(
        lambda: update_all_views(DB_CONFIG), 
        CronTrigger(day_of_week='sun', hour=2, minute=30)
    )

    try:
        # Start the scheduler
        scheduler.start()
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler shutdown successfully")

if __name__ == "__main__":
    main()