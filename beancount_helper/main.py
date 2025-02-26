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
import re
import time
import socket
import random
import argparse
import logging
import subprocess
import webbrowser
from pathlib import Path
from tool import AppDataPath
from typing import NoReturn, Tuple, Dict
from mapper import AccountMapper, BeancountMapper
from beancount_helper.conversion import BeancountHelper
from init import config_load, init_wechat_rule, init_alipay_rule


def parse_arguments() -> argparse.Namespace:
    """
    解析命令行参数.
    Returns:
        argparse.Namespace: 包含解析后的参数的命名空间对象.
    """
    parser = argparse.ArgumentParser(description="beancount_helper", add_help=False)

    parser.add_argument("-h", "--help", action="help", help="显示此帮助消息并退出")
    parser.add_argument(
        "-r",
        "--run",
        action="store_true",
        help="运行账单 GUI ",
    )
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

    args = parser.parse_args()

    if args.target_path:
        if not (args.account_type or args.to_beancount):
            parser.error(
                "-t/--target_path 必须与 -a/--account_type 或 -b/--to_beancount 其中一个组合使用"
            )
    return args


def is_port_available(port: int) -> bool:
    """
    检查指定端口是否可用。
    使用 socket 尝试连接到指定端口，如果连接失败，则端口可用。
    Args:
        port (int): 要检查的端口号。
    Returns:
        bool: 如果端口可用，返回 True；否则返回 False。
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def get_random_available_port(port_range: range) -> int:
    """
    从指定范围内随机选择一个可用端口。
    首先打乱端口范围的顺序，然后依次检查每个端口是否可用，返回第一个可用端口。
    Args:
        port_range (range): 要检查的端口范围。
    Returns:
        int: 第一个可用的端口号。
    Raises:
        ValueError: 如果指定范围内没有可用端口，抛出此异常。
    """
    shuffled_ports = list(port_range)
    random.shuffle(shuffled_ports)
    for port in shuffled_ports:
        if is_port_available(port):
            return port
    raise ValueError("No available ports found in the specified range.")


def start_fava(target_path: Path, port: int) -> subprocess.Popen:
    """
    启动 Fava 并返回进程对象。
    Args:
        target_path (Path): Beancount 文件的路径。
        port (int): Fava 要监听的端口号。
    Returns:
        subprocess.Popen: Fava 进程对象。
    """
    command = ["fava", "-p", str(port), str(target_path)]
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )
    return process


def monitor_fava_output(process: subprocess.Popen) -> Tuple[bool, str]:
    """
    监控 Fava 输出，检查是否成功启动或出现错误。
    逐行读取 Fava 的输出，检查是否包含启动成功的 URL 或错误信息。
    Args:
        process (subprocess.Popen): Fava 进程对象。
    Returns:
        Tuple[bool, str]: 如果 Fava 成功启动，返回 (True, url)；如果失败，返回 (False, error_message)。
    """
    url_pattern = re.compile(r"Starting Fava on (http[s]?://\S+)")
    error_pattern = re.compile(r"Error:")
    while True:
        line = process.stdout.readline()
        if not line:
            break
        print(line, end="")

        url_match = url_pattern.search(line)
        if url_match:
            url = url_match.group(1)
            print("Fava started successfully!")
            return True, url

        if error_pattern.search(line):
            error_message = f"Fava encountered an error: {line.strip()}"
            return False, error_message
    return False, "Fava did not start successfully. No URL or error detected."


def run_fava(target_path: Path) -> NoReturn:
    """
    启动 Fava 并处理端口分配和错误。
    主函数，负责选择可用端口、启动 Fava、监控输出，并在成功启动后打开默认浏览器。
    Args:
        target_path (Path): Beancount 文件的路径。
    """

    port_range = range(5000, 5100)
    port = get_random_available_port(port_range)
    fava_process = start_fava(target_path, port)
    status, message = monitor_fava_output(fava_process)
    if status:
        webbrowser.open(message)
        print("Press Ctrl+C to exit...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down Fava...")
    else:
        print(f"{message}")
        print("Shutting down Fava...")
        fava_process.terminate()
        fava_process.wait()


def account_map(
    target_path: Path,
    account_type: str,
    rules: Dict[str, str],
    temp_csv_path: Path,
) -> NoReturn:
    """
    根据账户类型和规则映射交易记录。
    Args:
        target_path (Path): 目标文件路径。
        account_type (str): 账户类型（如 "wechat" 或 "alipay"）。
        rules (Dict[str, Any]): 映射规则。
        temp_csv_path (Path): 临时 CSV 文件路径。
    """
    if account_type == "wechat":
        wechatRule = rules["wechat"]
        account_mapper = AccountMapper(
            target_file=target_path,
            map=wechatRule,
            output_file=temp_csv_path,
        )
        account_mapper.process_transactions()
    elif account_type == "alipay":
        alipayRule = rules["alipay"]
        account_mapper = AccountMapper(
            target_file=target_path,
            map=alipayRule,
            output_file=temp_csv_path,
        )
        account_mapper.process_transactions()


def csv_to_beancount(
    target_path: Path,
    bean_path: Path,
    out_bean_path: Path,
    log_obj: logging.Logger,
) -> NoReturn:
    """
    将 CSV 文件转换为 Beancount 文件。
    Args:
        target_path (Path): 目标 CSV 文件路径。
        bean_path (Path): Beancount 文件路径。
        out_bean_path (Path): 输出 Beancount 文件路径。
        log_obj (logging.Logger): 日志对象。
    Returns:
        NoReturn
    """
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

    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):

            handler.close()

            logger.removeHandler(handler)


def main():
    args = parse_arguments()
    app_config, rules, log_obj, config_path = config_load()
    bean_path = app_config["bean_path"]
    temp_csv_path = app_config["temp_csv"]
    out_bean_path = app_config["out_bean"]

    if args.run:
        print((config_path / "bean" / "moneybook.bean"))
        run_fava((config_path / "bean" / "moneybook.bean"))
        return

    if args.init:
        app_data_path = AppDataPath()
        close_and_remove_handlers(log_obj)
        app_data_path.create_directories(True)
        init_wechat_rule(config_path / "rule")
        init_alipay_rule(config_path / "rule")
        (config_path / "bean" / "moneybook.bean").touch()
        return

    if args.get_config:
        print(f"配置文件路径：{config_path}")
        return

    if args.target_path and args.account_type:
        account_map(args.target_path, args.account_type, rules, temp_csv_path)
        return

    if args.target_path and args.to_beancount:
        csv_to_beancount(args.target_path, bean_path, out_bean_path, log_obj)
        return


if __name__ == "__main__":
    main()
