# -*- coding: utf-8 -*-

import os
import logging
from logging.handlers import TimedRotatingFileHandler


# 创建一个字典来存储日志器
loggers = {}


def get_logger(logger_name, log_level, log_path):
    if logger_name in loggers:
        return loggers[logger_name]

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    handler = TimedRotatingFileHandler(os.path.join(log_path, f"{logger_name}.log"), when="MIDNIGHT")
    # formatter = logging.Formatter('%(asctime)s - %(thread)d - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(handler)

    loggers[logger_name] = logger

    return logger
