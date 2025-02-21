#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename : pipeline.py
@Author : ZouZhao
@Contact : wszwc3721@163.com
@Time : 2025/01/17 20:41
@License : Copyright (c) 2025 by ZouZhao, All Rights Reserved.
@Description : 管道
"""

__copyright__ = "Copyright (c) 2025 by ZouZhao, All Rights Reserved."
__license__ = None

from datetime import datetime
from typing import Callable, Dict

PipeFunc = Callable[[Dict], Dict]


def to_data(date_str_key: str, date_format: str) -> PipeFunc:
    """日期转换管道处理函数"""

    def _to_data(data: Dict) -> Dict:
        date_str = data[date_str_key]
        date_time_obj = datetime.strptime(date_str, date_format)
        data["date"] = date_time_obj.strftime("%Y/%m/%d")
        return data

    return _to_data


def to_amount(amount_key: str) -> PipeFunc:
    """金额转换管道处理函数"""

    def _to_amount(data: Dict) -> Dict:
        amount_str = data[amount_key]
        amount_str = "".join(filter(lambda x: x.isdigit() or x == ".", amount_str))
        data["amount"] = float(amount_str)
        return data

    return _to_amount


def to_remark(remark_keys: list) -> PipeFunc:
    """备注转换管道处理函数"""

    def _to_remark(data: Dict) -> Dict:
        remark_parts = [data[key] for key in remark_keys if data[key] != "/"]
        data["remark"] = " ".join(remark_parts)
        return data

    return _to_remark


def to_status(status_value: str) -> PipeFunc:
    """状态转换管道处理函数"""

    def _to_status(data: Dict) -> Dict:
        data["status"] = status_value
        return data

    return _to_status


def to_description(description_key: str) -> PipeFunc:
    """描述转换管道处理函数"""

    def _to_description(data: Dict) -> Dict:
        data["description"] = data[description_key]
        return data

    return _to_description


def to_currency(currency_value: str) -> PipeFunc:
    """货币转换管道处理函数"""

    def _to_currency(data: Dict) -> Dict:
        data["currency"] = currency_value
        return data

    return _to_currency
