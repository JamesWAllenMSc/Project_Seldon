""" Runs the database manager for the data center.
    Includes the following:
        - Daily updates of price and stock data
        - Monthly updates of global exchanges and new tickers
"""

# Standard library imports
from pathlib import Path
import time

# Local application imports
from lib.data_centre.database.scripts import daily_price_update
from config.connections.database_access import DB_CONFIG
from config.settings.logging import logger_factory

# Third party imports
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from lib.data_centre.database.scripts import (exchanges_update, 
                                              tickers_update, 
                                              update_all_views)

logger = logger_factory.get_logger('database', module_name=__name__)

def main():
    """ Main function to schedule tasks using APScheduler """
    logger.info("Starting Seldon database management scripts...")

    # Create a BackgroundScheduler
    scheduler = BackgroundScheduler()

    # Schedule `run_daily_updates` at 1:00 AM and 1:00 PM every day
    #scheduler.add_job(daily_price_update, CronTrigger(hour=1, minute=0))
    #scheduler.add_job(daily_price_update, CronTrigger(hour=13, minute=0))
    scheduler.add_job(daily_price_update, CronTrigger(minute='*/2'))

    # Schedule weekly tasks - Note: Don't call the functions, just pass them
    scheduler.add_job(
        lambda: exchanges_update(DB_CONFIG), 
        #CronTrigger(day_of_week='sun', hour=2, minute=0)
        CronTrigger(minute='*/3')
    )

    scheduler.add_job(
        tickers_update, 
        #CronTrigger(day_of_week='sun', hour=2, minute=15)
        CronTrigger(minute='*/4')
    )

    scheduler.add_job(
        lambda: update_all_views(DB_CONFIG), 
        #CronTrigger(day_of_week='sun', hour=2, minute=30)
        CronTrigger(minute='*/5')
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