from logging import config

log_config = {
    "version": 1,
    "handlers": {
        "console": {
            "formatter": "std_out",
            "class": "logging.StreamHandler",
            "level": "ERROR"
        },
        "file": {
            "formatter": "std_out",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "./measures.log",
            "backupCount": "3"
        }
    },
    "loggers": {
        "Measures": {
            "level": "ERROR",
            "handlers": ["console", "file"]
        },
        "MeasuresSQLPersister": {
            "level": "ERROR",
            "handlers": ["console", "file"]
        },
        "MeasureServer": {
            "level": "ERROR",
            "handlers": ["console", "file"]
        },
        "Main": {
            "level": "ERROR",
            "handlers": ["console", "file"]
        }
    },
    "formatters": {
        "std_out": {
            "format": "%(asctime)s : %(levelname)s : %(module)s :  %(message)s",
            "datefmt": "%d-%m-%Y %I:%M:%S"
        }
    },
}


def load_logging_config():
    config.dictConfig(log_config)
