import logging
import logging.handlers


def app_logging(config_obj, app_log_file):

    # read log levels
    log_level = config_obj["general"]["log_level"]

    # setup log formatting
    app_formatter = logging.Formatter("%(asctime)s :: [%(levelname)s] %(message)s")

    if log_level.lower() == "debug":

        # setup log formatting for debug
        app_formatter = logging.Formatter("%(asctime)s %(threadName)s %(module)s %(funcName)s :: [%(levelname)s] %(message)s")

    # setup logger for app
    app_logger = logging.getLogger("app")

    # add rotating log handler
    app_rotatingfilehandler = logging.handlers.RotatingFileHandler(app_log_file, "a", maxBytes=10485760, backupCount=3, encoding="utf-8")

    # set formatter for app
    app_rotatingfilehandler.setFormatter(app_formatter)

    # add the log message handler to the logger
    app_logger.addHandler(app_rotatingfilehandler)

    # set level of logging from config
    if log_level.lower() == "info":

        app_logger.setLevel(logging.INFO)

    elif log_level.lower() == "warning":

        app_logger.setLevel(logging.WARNING)

    elif log_level.lower() == "exception":

        app_logger.setLevel(logging.ERROR)

    elif log_level.lower() == "debug":

        app_logger.setLevel(logging.DEBUG)

    else:

        app_logger.setLevel(logging.WARNING)

    # setup logging to console
    console_streamhandler = logging.StreamHandler()

    # set formatter for console
    console_streamhandler.setFormatter(app_formatter)

    # add handler for formatter to the console
    app_logger.addHandler(console_streamhandler)

    # set level of logging from config
    if log_level.lower() == "info":

        console_streamhandler.setLevel(logging.INFO)

    elif log_level.lower() == "warning":

        console_streamhandler.setLevel(logging.WARNING)

    elif log_level.lower() == "exception":

        console_streamhandler.setLevel(logging.ERROR)

    elif log_level.lower() == "debug":

        console_streamhandler.setLevel(logging.DEBUG)

    else:

        console_streamhandler.setLevel(logging.WARNING)

    return {'logger': app_logger, 'handler': app_rotatingfilehandler}
