"""
Logs | Cannlytics
Copyright (c) 2024 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/8/2024
Updated: 12/8/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
from datetime import datetime
import logging
import os
import tempfile
from typing import Optional, Union


def initialize_logs(
        name: str,
        log_dir: Optional[Union[str, bool]] = 'D:\\data\\.logs',
        level: int = logging.DEBUG,
        prefix: Optional[str] = None,
        use_temp: bool = False,
        filemode: str = 'a',
        date_format: str = '%Y-%m-%dT%H:%M:%S'
    ) -> logging.Logger:
    """Configure a logger with file and console output.
    Args:
        name: Logger name (typically __name__)
        log_dir: Directory for log files. If False, only console logging is used
        level: Logging level (defaults to DEBUG like original function)
        prefix: Optional prefix for log filename
        use_temp: If True, use system temp directory instead of log_dir
        filemode: File mode for log file ('w+' for new file, 'a' for append)
        date_format: Format for timestamp in logs
    Returns:
        logging.Logger: Configured logger instance
    """
    # Clear any existing handlers.
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(level)
    
    # Create formatter.
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt=date_format
    )
    
    # Add console handler.
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)
    
    # Add file handler if logging to file is enabled.
    if log_dir:
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        prefix = f'{prefix}-' if prefix else ''
        if use_temp:
            log_dir = tempfile.gettempdir()
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f'{prefix}{timestamp}.log')
        file_handler = logging.FileHandler(log_file, mode=filemode)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
    logger.propagate = False
    return logger
