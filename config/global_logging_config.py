"""Global logging configuration for Project Seldon."""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

class LoggerFactory:
    """Factory class to create and manage loggers for different project areas."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
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
            # Create new logger
            logger = logging.getLogger(logger_name)
            logger.setLevel(level)
            
            # Only add handlers if they haven't been added
            if not logger.handlers:
                # Create area-specific log file
                log_file = self.log_dir / f"{area}_{datetime.now().strftime('%Y-%m-%d')}.log"
                
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

# Example usage in other modules:
# from config.global_logging_config import logger_factory
# logger = logger_factory.get_logger('database', module_name=__name__)