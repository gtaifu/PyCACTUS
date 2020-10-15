import logging
from logging import debug
from logging.handlers import TimedRotatingFileHandler
import sys
import colorama as cm
import termcolor as tc
from pathlib import Path, PurePath

cm.init()

# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

debug_mode = True


def pycactus_msg(arg, **kwargs):
    print(tc.colored(arg, 'green'), **kwargs)


def pycactus_debug(arg, **kwargs):
    if debug_mode:
        print(tc.colored(arg, 'yellow'), **kwargs)


def pycactus_err(arg, **kwargs):
    print(tc.colored(arg, 'red'), **kwargs)


# FORMATTER = logging.Formatter(
#     "%(asctime)s — %(name)s — %(levelname)s — %(message)s")
FORMATTER = logging.Formatter(
    "%(name)s %(lineno)d(%(levelname)s):  - %(message)s")


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler(log_file):
    file_handler = TimedRotatingFileHandler(log_file, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name, log_file=None):
    logger = logging.getLogger(logger_name)
    # better to have too much log than not enough
    logger.setLevel(logging.DEBUG)
    if log_file is None:
        logger.addHandler(get_console_handler())
    else:
        logger.addHandler(get_file_handler(log_file))

    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger
