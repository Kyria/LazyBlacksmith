import logging


class NullHandler(logging.Handler):

    def emit(self, record):
        pass

logger = logging.getLogger('pycrest')
logger.addHandler(NullHandler())

version = "0.0.5"

from .eve import EVE
