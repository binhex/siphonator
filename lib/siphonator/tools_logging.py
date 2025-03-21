import logging
import logging.handlers


def app_logging(log_level_file, log_level_console, logs_filepath):

    # File formatter
    file_formatter = logging.Formatter("%(asctime)s %(funcName)s :: [%(levelname)s] %(message)s")
    if log_level_file.lower() == "debug":
        file_formatter = logging.Formatter("%(asctime)s %(threadName)s %(module)s %(funcName)s :: [%(levelname)s] %(message)s")

    # Console formatter
    console_formatter = logging.Formatter("%(asctime)s %(funcName)s :: [%(levelname)s] %(message)s")
    if log_level_console.lower() == "debug":
        console_formatter = logging.Formatter("%(asctime)s %(threadName)s %(module)s %(funcName)s :: [%(levelname)s] %(message)s")

    # Setup logger for app
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.DEBUG)  # Set to the lowest level to capture all logs, handlers will filter

    # Add rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(logs_filepath, "a", maxBytes=10485760, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(file_formatter)
    app_logger.addHandler(file_handler)

    # Set level of logging for file handler
    if log_level_file.lower() == "info":
        file_handler.setLevel(logging.INFO)
    elif log_level_file.lower() == "warning":
        file_handler.setLevel(logging.WARNING)
    elif log_level_file.lower() == "error":
        file_handler.setLevel(logging.ERROR)
    elif log_level_file.lower() == "debug":
        file_handler.setLevel(logging.DEBUG)
    else:
        file_handler.setLevel(logging.WARNING)

    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    app_logger.addHandler(console_handler)

    # Set level of logging for console handler
    if log_level_console.lower() == "info":
        console_handler.setLevel(logging.INFO)
    elif log_level_console.lower() == "warning":
        console_handler.setLevel(logging.WARNING)
    elif log_level_console.lower() == "error":
        console_handler.setLevel(logging.ERROR)
    elif log_level_console.lower() == "debug":
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.WARNING)

    return app_logger, file_handler, console_handler
