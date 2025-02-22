#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename : main.py
@Author : ZouZhao
@Contact : wszwc3721@163.com
@Time : 2025/02/21 21:33
@License : Copyright (c) 2025 by ZouZhao, All Rights Reserved.
@Description : 主函数
"""

__copyright__ = "Copyright (c) 2025 by ZouZhao, All Rights Reserved."
__license__ = None

import argparse
import logging
from mapper import AccountMapper, BeancountMapper
from beancount_tool import BeancountHelper
from init import config_load, init_wechat_rule, init_alipay_rule
from tool import AppDataPath
from pathlib import Path
from typing import NoReturn


def parse_arguments() -> argparse.Namespace:
    """
    解析命令行参数.

    Returns:
        argparse.Namespace: 包含解析后的参数的命名空间对象.
    """

    parser = argparse.ArgumentParser(description="beancount_helper", add_help=False)
    # 解析参数
    parser.add_argument("-h", "--help", action="help", help="显示此帮助消息并退出")
    parser.add_argument(
        "-i",
        "--init",
        action="store_true",
        help="初始化应用，只能单独使用",
    )
    parser.add_argument(
        "-g",
        "--get_config",
        action="store_true",
        help="获取配置路径路径，只能单独使用",
    )
    parser.add_argument(
        "-t",
        "--target_path",
        type=str,
        help="目标文件路径，必须是 csv 格式",
    )
    parser.add_argument(
        "-a",
        "--account_type",
        type=str,
        choices=["wechat", "alipay"],
        help="账户映射类型，只支持 wechat 或 alipay",
    )
    parser.add_argument(
        "-b",
        "--to_beancount",
        action="store_true",
        help="将 csv 文件转换为 beancount 文件格式",
    )

    # 解析参数
    args = parser.parse_args()

    # 验证 --target_path 的逻辑约束
    if args.target_path:
        if not (args.account_type or args.to_beancount):
            parser.error(
                "-t/--target_path 必须与 -a/--account_type 或 -b/--to_beancount 其中一个组合使用"
            )

    return args


def account_map(target_path, account_type, rules, temp_csv_path):
    if account_type == "wechat":
        wechatRule = rules["wechat"]

        account_mapper = AccountMapper(
            target_file=target_path,
            map=wechatRule,
            output_file=temp_csv_path,
        )
        account_mapper.process_transactions()
    elif account_type == "alipay":
        alipayRule = rules["wechat"]

        account_mapper = AccountMapper(
            target_file=target_path,
            map=alipayRule,
            output_file=temp_csv_path,
        )
        account_mapper.process_transactions()


def csv_to_beancount(target_path, bean_path, out_bean_path, log_obj):
    beancount_mapper = BeancountMapper(target_path)
    transactions = beancount_mapper.map_to_transactions()
    beancount_helper = BeancountHelper(bean_path, out_bean_path, log_obj)
    beancount_helper.write_transaction_list(transactions)


def close_and_remove_handlers(logger: logging.Logger) -> NoReturn:
    """关闭并移除 Logger 对象中的所有 FileHandler 处理器，释放对日志文件的占用。

    Args:
        logger (logging.Logger): 类型的日志记录器对象

    Raises:
        ValueError: 提供的参数不是有效的 logging.Logger 对象

    Returns:
        NoReturn
    """
    if not isinstance(logger, logging.Logger):
        raise ValueError("提供的参数不是有效的 logging.Logger 对象")

    # 遍历所有处理器
    for handler in logger.handlers[:]:  # 使用切片避免修改列表时的迭代问题
        if isinstance(handler, logging.FileHandler):
            # 关闭文件句柄
            handler.close()
            # 移除处理器
            logger.removeHandler(handler)


def main():
    args = parse_arguments()
    app_config, rules, log_obj, config_path = config_load()
    bean_path = app_config["bean_path"]
    temp_csv_path = app_config["temp_csv"]
    out_bean_path = app_config["out_bean"]

    if args.init:
        app_data_path = AppDataPath()
        close_and_remove_handlers(log_obj)
        app_data_path.create_directories(True)
        init_wechat_rule(config_path / "rule")
        init_alipay_rule(config_path / "rule")
        (config_path / "bean" / "moneybook.bean").touch()
        return

    if args.get_config:
        print(f"配置文件路径{config_path}")
        return

    if args.target_path and args.account_type:
        account_map(args.target_path, args.account_type, rules, temp_csv_path)
        return

    if args.target_path and args.to_beancount:
        csv_to_beancount(args.target_path, bean_path, out_bean_path, log_obj)
        return


if __name__ == "__main__":
    main()
