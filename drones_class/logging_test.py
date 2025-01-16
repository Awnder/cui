import logging, logging.config
from datetime import datetime

# Create one log file for each hour of the day to balances the number of files
#   with the size of each file. If we run the drone multiple times within the
#   same hour, each run will be logged in the same file.
now = datetime.now().strftime("%Y%m%d.%H")
logfile = f"headsupflight.{now}.log"
logname = 'skeet'

# Thanks to Yogesh Yadav's example with Stream Handler and File Handler:
#   https://stackoverflow.com/questions/7507825 (not the winning answer)
# Configure the logger so that DEBUG messages and higher are logged to file but
#   only WARNINGS and higher are printed to stderr
log_settings = {
    'version':1,
    'disable_existing_loggers': False,
    'handlers': {
        'error_file_handler': {
            'level': 'DEBUG',
            'formatter': 'drone_errfile_fmt',
            'class': 'logging.FileHandler',
            'filename': logfile,
            'mode': 'a',
        },
        'debug_console_handler': {
            'level': 'WARNING',
            'formatter': 'drone_stderr_fmt',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },    
    },    
    'formatters': {
        'drone_errfile_fmt': {
            'format': '%(asctime)s|%(levelname)s: %(message)s [%(name)s@%(filename)s.%(funcName)s.%(lineno)d]',
            'datefmt': '%Y-%m-%dT%H:%M:%S'
        },
        'drone_stderr_fmt': {
            'format': '%(levelname)s: %(message)s [%(name)s@%(filename)s.%(funcName)s.%(lineno)d]',
        },
    },
    'loggers': {
        logname: {
            'handlers' :['debug_console_handler', 'error_file_handler'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Test the logger
logging.config.dictConfig(log_settings)
log = logging.getLogger(logname)
log.warning("This is my test log message")

