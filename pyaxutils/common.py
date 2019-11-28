import logging
logging.basicConfig()
logger = logging.getLogger(__package__ and __package__.name or "")


def debug(*args, **kwargs):
    logger.debug(*args, **kwargs)


def info(msg, *args, **kwargs):
    print("info")
    logger.info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    logger.warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    logger.error(msg, *args, **kwargs)


def exception(msg, *args, **kwargs):
    logger.exception(msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    logger.critical(msg, *args, **kwargs)


def log(level, msg, *args, **kwargs):
    logger.log(level, msg, *args, **kwargs)
