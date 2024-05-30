import logging
from logging.handlers import RotatingFileHandler


logger = logging.getLogger("Proxy logger")
logger.setLevel(logging.INFO)


__handler = RotatingFileHandler("proxy.log", maxBytes=1024**2, backupCount=4)
__formatter = logging.Formatter("[%(asctime)s - %(levelname)s - %(message)s]")

__handler.setFormatter(__formatter)
logger.addHandler(__handler)



