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
from tool import singleton
from config import Config


@singleton
class LoggerManager:
    _instance = None

    def __init__(
        self,
        name: str = Config.app_name,
        log_dir: str = Config.log_path,
        level: int = Config.log_level,
    ):
        self.name = name
        self.log_dir = log_dir
        self.level = level
        self._setup_logger()

    def _setup_logger(self):
        # 确保日志目录存在
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # 创建 logger
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)

        # 配置控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            colorlog.ColoredFormatter(
                Config.log_fmt, Config.log_datefmt, Config.log_colors
            )
        )
        logger.addHandler(console_handler)

        # 配置文件处理器
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
            logging.Formatter(Config.log_fmt, Config.log_datefmt, Config.log_colors)
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
