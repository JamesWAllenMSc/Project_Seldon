"""Global logging configuration for Project Seldon."""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# Get project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOG_DIR = PROJECT_ROOT / "logs"

class LoggerFactory:
    """Factory class to create and manage loggers for different project areas."""
    
    def __init__(self):
        self.log_dir = LOG_DIR
        self.log_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different areas
        self.log_dir.joinpath('database').mkdir(exist_ok=True)
        self.log_dir.joinpath('global').mkdir(exist_ok=True)
        
        self._loggers = {}

    def get_logger(
        self, 
        area: str, 
        level: int = logging.INFO,
        module_name: Optional[str] = None
    ) -> logging.Logger:
        """
        Get or create a logger for a specific project area.
        
        Args:
            area: Project area (e.g., 'database', 'analysis', 'api')
            level: Logging level
            module_name: Optional module name for logger identification
        """
        logger_name = f"{area}_{module_name}" if module_name else area
        
        if logger_name not in self._loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(level)
            
            if not logger.handlers:
                # Simplified log file naming: area_YYYY_DD.log
                log_file = self.log_dir / area / f"{area}_{datetime.now().strftime('%Y_%d')}.log"
                
                log_file.parent.mkdir(exist_ok=True)
                
                # File handler
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(level)
                file_formatter = logging.Formatter(
                    'Datetime:%(asctime)s - Level:%(levelname)s - '
                    'Module:%(module)s - Function:%(funcName)s - '
                    'Message:%(message)s'
                )
                file_handler.setFormatter(file_formatter)
                
                # Console handler
                console_handler = logging.StreamHandler()
                console_handler.setLevel(level)
                console_formatter = logging.Formatter(
                    '%(levelname)s [%(name)s]: %(message)s'
                )
                console_handler.setFormatter(console_formatter)
                
                # Add handlers
                logger.addHandler(file_handler)
                logger.addHandler(console_handler)
                
                self._loggers[logger_name] = logger
        
        return self._loggers[logger_name]

# Create global logger factory instance
logger_factory = LoggerFactory()