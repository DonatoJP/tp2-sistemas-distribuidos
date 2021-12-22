import logging, os

logging.getLogger("pika").setLevel(logging.WARNING)
# logging.getLogger("pika").propagate = False
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(format='%(asctime)s-%(process)d-%(name)s-%(levelname)s-%(message)s', level=LOGLEVEL)
logger = logging.getLogger(__name__)