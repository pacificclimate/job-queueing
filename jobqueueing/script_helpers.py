"""
Helpers for defining a script.
"""
import logging


formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', "%Y-%m-%d %H:%M:%S")
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger('JQ')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)  # For testing, overridden when run as a script