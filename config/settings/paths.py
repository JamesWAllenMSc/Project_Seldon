import os
import sys
from pathlib import Path

# Get the project root directory (3 levels up from this file)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

PATHS = {
    "PROJECT_ROOT": PROJECT_ROOT,
    "DATABASE": PROJECT_ROOT / "lib/data_centre/database",
    #"DATABASE_CONFIG": PROJECT_ROOT / "lib/data_centre/database/config/database_config.py",
    #"DATABASE_MANAGER": PROJECT_ROOT / "lib/data_centre/database/database_manager.py",
    #"LOGS_DIR": PROJECT_ROOT / "logs",
    #"DATA_DIR": PROJECT_ROOT / "data",
    #"OUTPUT_DIR": PROJECT_ROOT / "output",
}

# Add project root to system path if not already present
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
