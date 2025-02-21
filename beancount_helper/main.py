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

from log import LoggerManager

if __name__ == "__main__":

    singleton_logger = LoggerManager()
    logger = singleton_logger.get_logger()
