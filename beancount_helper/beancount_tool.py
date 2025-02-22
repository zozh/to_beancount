#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename : beancount_tool.py
@Author : ZouZhao
@Contact : wszwc3721@163.com
@Time : 2024/12/28 15:51
@License : Copyright (c) 2024 by ZouZhao, All Rights Reserved.
@Description : Beancount 助手
"""

__copyright__ = "Copyright (c) 2025 by ZouZhao, All Rights Reserved."
__license__ = None

import os
import logging
import tempfile
import subprocess
from beancount import loader
from typing import NoReturn, List, Tuple
from dataclasses import dataclass, fields


@dataclass
class Transaction:
    """Beancount 交易数据类"""

    date: str = None
    status: str = None
    description: str = None
    debit: str = None
    credit: str = None
    amount: float = None
    currency: str = None
    remark: str = None
    index: str = None

    def __str__(self) -> str:
        return self.get_str()

    def get_str(self) -> str:
        """Beancount 交易字符串

        Returns:
            str: 转换后的字符串
        """
        one = f'\n{self.date} {self.status} "{self.description}" "{self.remark}"\n'
        two = f"\t{self.debit}\t\t\t{self.amount} {self.currency}\n"
        three = f"\t{self.credit}\t\t\t-{self.amount} {self.currency}\n"
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


class BeancountHelper:
    """Beancount 工具类"""

    def __init__(
        self, file_path: str, log_obj: logging.Logger, out_format: str
    ) -> NoReturn:
        self._file_path = file_path
        self._entries, self._errors, self._options_map = self._load(file_path)
        self.log_obj = log_obj
        self.out_format = out_format

    def _load(self, file_path: str) -> tuple:
        """加载文件 Beancount

        Args:
            file_path (str): Beancount 文件路径

        Raises:
            ValueError: 解析失败抛出

        Returns:
            tuple(entries,errors,options_map)
            entries 按日期排序的条目列表
            errors 生成的错误对象列表
            options_map 对象的字典
        """
        entries, errors, options_map = loader.load_file(file_path)

        if errors:
            for error in errors:
                self.log_obj.error(f"={error}")
            raise ValueError(file_path, "Invalid file format")
        return entries, errors, options_map

    def write_transaction_list(self, transaction_list: List[Transaction]) -> bool:
        """
        向 Beancount 文件写入 Transaction 列表，并进行格式验证和回滚。

        Args:
            transaction_list (List[Transaction]): 交易数据类列表。

        Returns:
            bool: 写入成功返回 True，否则返回 False。
        """
        try:
            # 获取 Beancount 文件所在目录
            beancount_dir = os.path.dirname(os.path.abspath(self._file_path))

            # 在 Beancount 文件所在目录创建临时文件
            with tempfile.NamedTemporaryFile(
                mode="w+",
                delete=False,
                suffix=".bean",
                dir=beancount_dir,
                encoding="utf-8",
            ) as temp_file:
                temp_file_path = temp_file.name

                # 写入交易记录
                for transaction in transaction_list:
                    temp_file.write(transaction.get_str())

            # 验证 Beancount 文件格式
            is_valid, _ = self._check_syntax()
            if not is_valid:
                self.log_obj.error("写入的交易记录导致文件格式无效，正在进行回滚...")
                self._rollback_include(temp_file_path)
                return False

            # 如果验证通过，重命名临时文件为唯一名称
            new_file_name = f"{self.out_format}.bean"
            new_file_path = os.path.join(beancount_dir, new_file_name)

            # 添加日志记录
            self.log_obj.debug(f"Beancount 目录: {beancount_dir}")
            self.log_obj.debug(f"临时文件路径: {temp_file_path}")
            self.log_obj.debug(f"新文件路径: {new_file_path}")

            os.rename(temp_file_path, new_file_path)

            # 更新 include 行
            include_line = (
                f'include "{os.path.relpath(new_file_path, start=beancount_dir)}"\n'
            )
            with open(self._file_path, "a", encoding="utf-8") as main_file:
                main_file.write("\n;【新增交易记录】\n")
                main_file.write(include_line)

            self.log_obj.info("交易记录写入成功！")
            return True

        except Exception as e:
            self.log_obj.error(f"写入交易记录时发生错误: {e}")
            return False

    def _rollback_include(self, temp_file_path: str) -> None:
        """
        回滚 include 引入的临时文件。

        Args:
            temp_file_path (str): 临时文件路径。
        """
        # 删除 include 行
        lines = []
        with open(self._file_path, "r", encoding="utf-8") as main_file:
            lines = main_file.readlines()

        with open(self._file_path, "w", encoding="utf-8") as main_file:
            for line in lines:
                if not line.strip().startswith(
                    f'include "{os.path.basename(temp_file_path)}"'
                ):
                    main_file.write(line)

        # 删除临时文件
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        self.log_obj.info("回滚完成！")

    def _check_syntax(self) -> Tuple[bool, str]:
        """检查 Beancount 文件格式。

        Returns:
            Tuple[bool, str]: (是否有效, 错误信息或 "Successful")
        """
        command = ["bean-check", self._file_path]
        result = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8"
        )

        if result.stderr:
            self.log_obj.error(f"格式检查失败: {result.stderr}")
            return False, result.stderr
        else:
            self.log_obj.info("格式检查成功！")
            return True, "Successful"
