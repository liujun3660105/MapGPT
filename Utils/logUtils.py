from typing import Optional,cast
import logging
import logging.handlers
import os
from config.config import LOGDIR


handler = None
def logging_str_to_uvicorn_level(log_level_str):
    level_str_mapping = {
        "CRITICAL": "critical",
        "ERROR": "error",
        "WARNING": "warning",
        "INFO": "info",
        "DEBUG": "debug",
        "NOTSET": "info",
    }
    return level_str_mapping.get(log_level_str.upper(), "info")

def _get_logging_level() -> str:
    return os.getenv("DBGPT_LOG_LEVEL", "INFO")

def setup_logging_level(
    logging_level: Optional[str] = None, logger_name: Optional[str] = None
):
    if not logging_level:
        logging_level = _get_logging_level()
    if type(logging_level) is str:
        logging_level = logging.getLevelName(logging_level.upper())
    if logger_name:
        logger = logging.getLogger(logger_name)
        logger.setLevel(cast(str, logging_level))
    else:
        logging.basicConfig(level=logging_level, encoding="utf-8")


def setup_logging(
    logger_name: str,
    logging_level: Optional[str] = None,
    logger_filename: Optional[str] = None,
):
    if not logging_level:
        logging_level = _get_logging_level()
    logger = _build_logger(logger_name, logging_level, logger_filename)
    try:
        import coloredlogs

        color_level = logging_level if logging_level else "INFO"
        coloredlogs.install(level=color_level, logger=logger)
    except ImportError:
        pass
    
def _build_logger(
    logger_name,
    logging_level: Optional[str] = None,
    logger_filename: Optional[str] = None,
):
    global handler

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Set the format of root handlers
    if not logging.getLogger().handlers:
        setup_logging_level(logging_level=logging_level)
    logging.getLogger().handlers[0].setFormatter(formatter)

    # Add a file handler for all loggers
    if handler is None and logger_filename:
        os.makedirs(LOGDIR, exist_ok=True)
        filename = os.path.join(LOGDIR, logger_filename)
        handler = logging.handlers.TimedRotatingFileHandler(
            filename, when="D", utc=True
        )
        handler.setFormatter(formatter)

        for name, item in logging.root.manager.loggerDict.items():
            if isinstance(item, logging.Logger):
                item.addHandler(handler)
    # Get logger
    logger = logging.getLogger(logger_name)
    setup_logging_level(logging_level=logging_level, logger_name=logger_name)

    return logger