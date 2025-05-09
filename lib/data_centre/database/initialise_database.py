""" Start up script to set up all database tables and initial historical
    data.
"""
#
import sys

from config.database_config import PATHS
from mysql.connector import connect, Error
from config.database_access_config import DB_CONFIG
from utils import database_utils


# Set up the project root path
project_root = PATHS['DATABASE']
sys.path.append(project_root)


database_utils.clear_all_tables(DB_CONFIG)

