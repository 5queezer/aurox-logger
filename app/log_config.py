import os
from logging import FileHandler
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s.%(msecs)06d %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "debug": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s.%(msecs)06d - %(filename)30s:%(lineno)4d - %(message)s'",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "file": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s.%(msecs)06d - %(message)s'",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "debug": {
            "level": "DEBUG",
            "formatter": "debug",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "error": {
            "level": "ERROR",
            "formatter": "file",
            "class": "logging.FileHandler",
            "filename": "log/errors.log",
            "mode": "a"
        },
        "access": {
            "level": "INFO",
            "formatter": "file",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "log/access.log",
            "mode": "a",
            'maxBytes': 1048576,
            'backupCount': 10
        },
    },
    "loggers": {
        "app.main": {"handlers": ["default", "access"], "level": os.environ.get("LOG_LEVEL", "INFO")},
        "app.middleware": {"handlers": ["debug", "error"], "level": os.environ.get("LOG_LEVEL", "ERROR")},
    },
}
