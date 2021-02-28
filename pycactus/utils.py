import logging
from logging import debug
from logging.handlers import TimedRotatingFileHandler
import sys
import colorama as cm
import termcolor as tc
from pathlib import Path, PurePath
import time
cm.init()

# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

debug_mode = True

log_file = None


def pycactus_msg(arg, **kwargs):
    print(tc.colored(arg, 'green'), **kwargs)


def pycactus_debug(arg, **kwargs):
    if debug_mode:
        print(tc.colored(arg, 'yellow'), **kwargs)


def pycactus_err(arg, **kwargs):
    print(tc.colored(arg, 'red'), **kwargs)


# FORMATTER = logging.Formatter(
#     "%(asctime)s — %(name)s — %(levelname)s — %(message)s")
# FORMATTER = logging.Formatter(
#     "%(name)s %(lineno)d(%(levelname)s):  - %(message)s")
FORMATTER = logging.Formatter("%(message)s")


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler(log_file):
    file_handler = TimedRotatingFileHandler(log_file, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def set_logger_file():
    global log_file
    if (log_file is None):
        cur_time = time.strftime("%H_%M_%S", time.localtime())
        log_file = 'build/pycactus_' + cur_time + '.log'


def update_log_file(log_filename=None):
    if log_filename is None:
        cur_time = time.strftime("%H_%M_%S", time.localtime())
        log_filename = 'build/pycactus_' + cur_time + '.log'

    fileh = logging.FileHandler(log_filename, 'w')
    fileh.setFormatter(FORMATTER)

    global loggers
    for logname in loggers:
        log = logging.getLogger(logname)  # root logger
        for hdlr in log.handlers[:]:  # remove all old handlers
            log.removeHandler(hdlr)
        log.addHandler(fileh)      # set the new handler


loggers = []


def get_logger(logger_name):
    global loggers
    if (logger_name not in loggers):
        loggers.append(logger_name)

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
