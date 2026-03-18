import logging
from logging.handlers import TimedRotatingFileHandler  
import definitions
import config.config as config

_is_setup = False

def setup_logger():
    """
    Only call this once, in the main.
    This will rotate logs based on time intervals.
    Due to some limitation on naming, the log will be named with ".log" twice (app.log.[date].log)
    This is so that the current and archived logs have ".log" file type.
    Files with ".log" file type have syntax highlighting in IDE's and code editors.
    """
    global _is_setup
    
    if _is_setup is False:
        LOG_FORMATTER = logging.Formatter(config.LOG_FORMATTER_FORMAT)

        # Configure the TimeRotatingFileHandler.
        rotating_file_handler = TimedRotatingFileHandler(
            filename=definitions.LOG_OUTPUT_PATH,
            when=config.LOG_WHEN, # Rotate logs at midnight
            interval=config.LOG_INTERVAL, # Rotate every interval "when"
            backupCount=config.LOG_BACKUP_COUNT, # Number of logs to keep in the rotation.
            encoding="utf-8"
        )
        rotating_file_handler.suffix += ".log"
        rotating_file_handler.setLevel(logging.DEBUG)
        rotating_file_handler.setFormatter(LOG_FORMATTER)

        # Create a StreamHandler. This is for printing the logs in the console as well.
        console_log_handler = logging.StreamHandler()
        console_log_handler.setLevel(logging.DEBUG)
        console_log_handler.setFormatter(LOG_FORMATTER)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(rotating_file_handler)
        root_logger.addHandler(console_log_handler)

        _is_setup = True
    else:
        raise Exception("You are trying to setup a logger that is already setup.")