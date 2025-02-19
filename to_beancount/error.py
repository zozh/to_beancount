#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename : exception.py
@Author : ZouZhao
@Contact : wszwc3721@163.com
@Time : 2025/01/02 23:46
@License : Copyright (c) 2025 by ZouZhao, All Rights Reserved.
@Description :
"""

__copyright__ = "Copyright (c) 2025 by ZouZhao, All Rights Reserved."
__license__ = None


class FileParseError(Exception):
    """自定义文件解析异常"""

    def __init__(self, filename, message):
        self.filename = filename
        self.message = message
        super().__init__(f"Error parsing file {filename}: {message}")


class TransactionParseError(Exception):
    """自定义 Transaction 解析异常"""

    def __init__(self, message):
        self.message = message
        super().__init__(f"Error parsing Transaction : {message}")
