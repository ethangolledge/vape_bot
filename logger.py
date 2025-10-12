import logging
import os
from datetime import datetime

def setup_logger(filename: str) -> logging.Logger:
    logger = logging.getLogger(filename)
    logger.setLevel(logging.INFO)
    
    if logger.handlers:
        logger.handlers.clear()
    
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    try:
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f'{filename}.log')
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logger initialised at {datetime.now()}")
        
    except Exception as e:
        print(f"Failed to setup file handler: {e}")
        print(f"Attempted log directory: {log_dir}")
    
    return logger