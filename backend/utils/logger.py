import logging
logger = logging.getLogger('myapp')
logger.setLevel(logging.INFO)

# Create a file handler and add it to the logger
handler = logging.FileHandler('logger_app.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
