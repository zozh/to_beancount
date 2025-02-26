#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename : log.py
@Author : ZouZhao
@Contact : wszwc3721@163.com
@Time : 2025/02/21 21:33
@License : Copyright (c) 2025 by ZouZhao, All Rights Reserved.
@Description : 日志
"""

__copyright__ = "Copyright (c) 2025 by ZouZhao, All Rights Reserved."
__license__ = None

import os
import logging
import colorlog
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Dict
from tool import SingletonMeta


class LoggerManager(metaclass=SingletonMeta):
    _instance = None

    def __init__(
        self,
        name: str,
        log_dir: str,
        level: int,
        log_fmt: str,
        log_datefmt: str,
        log_colors: Dict[str, str],
    ):
        """
        初始化日志管理器。

        Args:
            name (str): 日志记录器名称。
            log_dir (str): 日志文件存储目录。
            level (int): 日志级别。
            log_fmt (str): 日志格式。
            log_datefmt (str): 日期格式。
            log_colors (Dict[str, str]): 日志颜色配置。
        """

        if hasattr(self, "initialized"):
            return

        self.name = name
        self.log_dir = log_dir
        self.level = level
        self.log_fmt = log_fmt
        self.log_datefmt = log_datefmt
        self.log_colors = log_colors

        self.initialized = True

        self._setup_logger()

    def _setup_logger(self):

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            colorlog.ColoredFormatter(
                fmt=self.log_fmt,
                datefmt=self.log_datefmt,
                log_colors=self.log_colors,
            )
        )
        logger.addHandler(console_handler)

        log_file = os.path.join(
            self.log_dir, f'log_{datetime.now().strftime("%Y-%m-%d")}.log'
        )
        file_handler = RotatingFileHandler(
            filename=log_file,
            mode="a",
            maxBytes=1048576,
            backupCount=7,
            encoding="utf-8",
        )
        file_handler.setFormatter(
            logging.Formatter(fmt=self.log_fmt, datefmt=self.log_datefmt)
        )
        logger.addHandler(file_handler)

        self.logger = logger

    def get_logger(self):
        return self.logger


if __name__ == "__main__":
    logger_manager = LoggerManager(
        name="my_module_logger", log_dir="logs", level=logging.DEBUG
    )
    logger = logger_manager.get_logger()

    logger.info("这是一个信息日志")
    logger.error("这是一个错误日志")
