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
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "debug": {
            "formatter": "debug",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "error": {
            "formatter": "file",
            "class": "logging.FileHandler",
            "filename": "log/errors.log",
        },
        "access": {
            "formatter": "file",
            "class": "logging.FileHandler",
            "filename": "log/access.log",
        },
    },
    "loggers": {
        "app.main": {"handlers": ["default", "access"], "level": os.environ.get("LOG_LEVEL", "INFO")},
        "app.middleware": {"handlers": ["debug", "error"], "level": os.environ.get("LOG_LEVEL", "ERROR")},
    },
}
