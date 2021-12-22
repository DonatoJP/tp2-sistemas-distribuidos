import logging, os

logging.getLogger("pika").setLevel(logging.WARNING)
# logging.getLogger("pika").propagate = False
logging.getLogger().setLevel(logging.FATAL)
# logging.basicConfig(level=logging.FATAL)
# logging.disable(level=logging.CRITICAL)
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
# logging.basicConfig(format='%(asctime)s-%(process)d-%(name)s-%(levelname)s-%(message)s', level=LOGLEVEL)
def create_logger(name):
    logger =  logging.getLogger(name)
    logger.setLevel(LOGLEVEL)
    logger.propagate = 0
    if not logger.handlers:
        logFormatter = logging.Formatter("%(asctime)s [%(filename)s] [%(funcName)s] [%(levelname)s] [%(lineno)d] %(message)s")
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        logger.addHandler(consoleHandler)
    return logger