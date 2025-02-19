#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename : beancount_tool.py
@Author : ZouZhao
@Contact : wszwc3721@163.com
@Time : 2024/12/28 15:51
@License : Copyright (c) 2024 by ZouZhao, All Rights Reserved.
@Description :
"""

__copyright__ = "Copyright (c) 2025 by ZouZhao, All Rights Reserved."
__license__ = None

import os
import time
import shutil
import subprocess
from pathlib import Path
from typing import NoReturn, List, Tuple
from dataclasses import dataclass, fields

from beancount import loader
from beancount.core.data import Open

from error import FileParseError
from log import get_logger

log_obj = get_logger()
module_name = Path(__file__).stem


@dataclass
class Transaction:
    """Beancount 交易数据类"""

    date: str = None
    status: str = None
    description: str = None
    in_account: str = None
    out_account: str = None
    amount: float = None
    currency: str = None
    remark: str = None
    index: str = int

    def __str__(self) -> str:
        return self.get_str()

    def get_str(self) -> str:
        """Beancount 交易字符串

        Returns:
            str: 转换后的字符串
        """
        one = f'\n{self.date} {self.status} "{self.description}" "{self.remark}"\n'
        two = f"\t{self.in_account}\t\t\t{self.amount} {self.currency}\n"
        three = f"\t{self.out_account}\t\t\t-{self.amount} {self.currency}\n"
        return one + two + three

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """
        从字典创建 Transaction 对象。

        Args:
            data (dict): 包含字段值的字典。

        Returns:
            Transaction: 初始化的 Transaction 对象。
        """
        # 获取所有字段名称
        field_set = {f.name for f in fields(cls)}
        # 过滤掉字典中不存在于字段中的键，并将字段名映射到字典值
        filtered_data = {k: v for k, v in data.items() if k in field_set}
        return cls(**filtered_data)


class BeancountTool:
    """Beancount 工具类"""

    def __init__(self, file_path: str) -> NoReturn:
        self._file_path = file_path
        self._entries, self._errors, self._options_map = self._load(file_path)
        self._account_list = []
        self._backup_path = file_path + ".backup"

    def _backup_file(self) -> NoReturn:
        """备份 Beancount 文件

        Returns:
            NoReturn
        """
        shutil.copy(self._file_path, self._backup_path)

    def _restore_backup(self) -> NoReturn:
        """恢复 Beancount 文件备份

        Returns:
            NoReturn
        """
        shutil.copy(self._backup_path, self._file_path)

    def _load(self, file_path: str) -> tuple:
        """加载文件 Beancount

        Args:
            file_path (str): Beancount 文件路径

        Raises:
            FileParseError: 解析失败抛出

        Returns:
            tuple(entries,errors,options_map)
            entries 按日期排序的条目列表
            errors 生成的错误对象列表
            options_map 对象的字典
        """
        entries, errors, options_map = loader.load_file(file_path)

        if errors:
            for error in errors:
                log_obj.error(f"[{module_name}] {error}")
            raise FileParseError(file_path, "Invalid file format")
        return entries, errors, options_map

    def _check_syntax(self) -> Tuple[str, bool]:
        """检查格式

        Returns:
            Tuple(str, bool):
        """
        command = ["bean-check", self._file_path]
        result = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8"
        )

        if result.stderr:
            return result.stderr, False
        else:
            return "Successful", True

    def get_account_info(self, entries: Open) -> NoReturn:
        """获得账户信息列表

        Args:
            entries (Open): 按日期排序的条目列表

        Returns:
            NoReturn
        """
        for entry in entries:
            if isinstance(entry, Open):
                self._account_list.append(entry.account)

    def write_transaction_list(self, transaction_list: List[Transaction]) -> NoReturn:
        """向 Beancount 文件写入 Transaction 列表，并进行格式验证和回滚

        Args:
            transaction_list (List[Transaction]): 交易数据类

        Returns:
            NoReturn
        """
        # 备份原始文件
        self._backup_file()

        try:
            # 写入交易数据
            with open(self._file_path, "a", encoding="utf-8") as file_obj:
                now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                file_obj.write(f"\n; to_beancount {now_time} start\n")

                for transaction in transaction_list:
                    file_obj.write(transaction.get_str())
                file_obj.write(f"\n; to_beancount {now_time} end\n")

            result, status = self._check_syntax()
            if not status:
                raise ValueError(result)
        except Exception as error:
            # 发生其他异常，回滚文件并抛出异常
            self._restore_backup()
            log_obj.error(f"[{module_name}] {error}")

        finally:
            # 删除备份文件
            os.remove(self._backup_path)
