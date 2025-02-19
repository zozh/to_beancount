import os
import logging
import colorlog
from logging.handlers import RotatingFileHandler
from datetime import datetime
from tool import singleton


@singleton
class LoggerManager:
    _instance = None

    def __init__(
        self, name: str = "default_logger", log_dir: str = "logs", level=logging.DEBUG
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
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red",
                },
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
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
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
