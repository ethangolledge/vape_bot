import logging
import os

def setup_logger(filename: str) -> logging.Logger:
    logger = logging.getLogger(filename)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    
    # add handler
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    # file handler and ionitalise logs dir
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(log_dir, f'{filename}.log'))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger