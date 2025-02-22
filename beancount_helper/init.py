import logging
from pathlib import Path
from log import LoggerManager
from config import config
from typing import Tuple, NoReturn


def ensure_directory_exists(path: Path) -> NoReturn:
    """
    确保指定的路径存在，如果不存在则创建。

    Args:
        path (Path): 要检查和创建的路径。

    Returns:
        NoReturn:

    Example:
        root_path = Path("/data/")
        ensure_directory_exists(root_path)
    """
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def init_app() -> Tuple[dict, logging.Logger, Path, str]:
    """
    初始化应用程序的基本组件。

    此函数加载配置文件，初始化日志管理器，确保根目录存在，并生成文件格式字符串。

    Returns:
        Tuple[dict, logging.Logger, Path, str]:
            包含以下四个元素的元组：
            - dict: 全局单例配置实例。
            - logging.Logger: 全局单例日志记录器实例。
            - Path: 根目录路径。
            - str: 文件格式字符串。

    Example:
        config_loader, log_obj, root_path, file_format = init_app()
    """
    # 确保根目录存在
    root_path = Path("/data/")
    ensure_directory_exists(root_path)

    # 初始化日志管理器
    log = config["app"]["log"]
    singleton_logger = LoggerManager(
        name=config["app"]["name"],
        log_dir=log["path"],
        level=log["level"],
        log_fmt=log["fmt"],
        log_datefmt=log["datefmt"],
        log_colors=log["colors"],
    )
    log_obj: logging.Logger = singleton_logger.get_logger()

    return config, log_obj, root_path
