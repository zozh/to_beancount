import pandas as pd
import logging
from pathlib import Path
from log import LoggerManager
from config import configs
from typing import Tuple, NoReturn, List
from tool import AppDataPath


def convert_relative_paths_to_absolute(config: dict, path_converter) -> dict:
    """
    递归遍历配置字典，将所有以 'data/' 开头的相对路径转换为绝对路径。

    Args:
        config (dict): 配置字典。
        path_converter (callable): 用于转换路径的可调用对象（如函数）。

    Returns:
        dict: 转换后的配置字典。
    """
    if isinstance(config, dict):
        # 如果是字典，递归处理每个键值对
        for key, value in config.items():
            if isinstance(value, str) and value.startswith("data/"):
                # 如果值是以 'data/' 开头的字符串，调用 path_converter 转换为绝对路径
                config[key] = str(path_converter(value))
            elif isinstance(value, (dict, list)):
                # 如果值是字典或列表，递归处理
                convert_relative_paths_to_absolute(value, path_converter)
    elif isinstance(config, list):
        # 如果是列表，递归处理每个元素
        for i, item in enumerate(config):
            if isinstance(item, str) and item.startswith("data/"):
                # 如果元素是以 'data/' 开头的字符串，调用 path_converter 转换为绝对路径
                config[i] = str(path_converter(item))
            elif isinstance(item, (dict, list)):
                # 如果元素是字典或列表，递归处理
                convert_relative_paths_to_absolute(item, path_converter)
    return config


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


def config_load() -> Tuple[dict, logging.Logger, Path, str]:
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
    # 初始化日志管理器
    app = configs["app"]
    log = app["log"]
    app_data_path = AppDataPath(app["name"], app["data_subdirectory"])
    config = convert_relative_paths_to_absolute(
        configs, app_data_path.get_absolute_path
    )

    singleton_logger = LoggerManager(
        name=app["name"],
        log_dir=log["path"],
        level=log["level"],
        log_fmt=log["fmt"],
        log_datefmt=log["datefmt"],
        log_colors=log["colors"],
    )
    log_obj = singleton_logger.get_logger()

    return (app, config["rules"], log_obj, app_data_path.get_path())


def init_xlsx(
    expenses_columns: List[str], assets_columns: List[str], target_path: Path
) -> NoReturn:
    """初始化 xlsx 表

    Args:
        expenses_columns (List[str]): expenses 表的列
        assets_columns (List[str]): assets 表的列
        target_path (Path): 目标路径

    Returns:
        NoReturn
    """
    # 创建Expenses工作表
    expenses_df = pd.DataFrame(columns=expenses_columns)
    # 创建Assets工作表
    assets_df = pd.DataFrame(columns=assets_columns)
    # 导出到Excel
    with pd.ExcelWriter(target_path) as writer:
        expenses_df.to_excel(writer, sheet_name="Expenses", index=False)
        assets_df.to_excel(writer, sheet_name="Assets", index=False)


def init_wechat_rule(root):
    """初始化 wechat_rule.xlsx

    Args:
        root (Path): 规则存放路径
    """
    init_xlsx(
        ["编号", "交易类型", "交易对方", "商品", "值", "备注"],
        ["编号", "交易类型", "支付方式", "当前状态", "值", "备注"],
        root / "wechat_rule.xlsx",
    )


def init_alipay_rule(root: Path):
    """初始化 alipay_rule.xlsx

    Args:
        root (Path): 规则存放路径
    """
    init_xlsx(
        ["编号", "交易分类", "交易对方", "商品说明", "值", "备注"],
        ["编号", "收/付款方式", "值", "备注"],
        root / "alipay_rule.xlsx",
    )
