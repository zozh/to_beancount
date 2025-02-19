#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename : pipeline.py
@Author : ZouZhao
@Contact : wszwc3721@163.com
@Time : 2025/01/17 20:41
@License : Copyright (c) 2025 by ZouZhao, All Rights Reserved.
@Description :
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


def apply_rules(tree) -> PipeFunc:
    """
    应用规则管道处理函数。

    Args:
        tree (Tree): 包含规则匹配逻辑的树对象。

    Returns:
        PipeFunc: 一个管道函数，用于根据规则树匹配并更新数据。
    """

    def _apply_rules(data: Dict) -> Dict:
        """
        根据规则树匹配并更新数据。

        Args:
            data (Dict): 输入的数据字典，包含需要匹配的字段。

        Returns:
            Dict: 更新后的数据字典。
        """
        # 假设数据中有一个字段表示匹配路径（例如 "path"）
        match_path = [data.get("交易类型"), data.get("交易对方"), data.get("商品")]
        if not isinstance(match_path, list):
            raise ValueError("数据中的 'path' 字段必须是一个列表")

        # 使用树结构进行匹配
        matched_result = tree.match(match_path)

        # 将匹配结果更新到数据字典中
        data["matched_category"] = matched_result

        return data

    return _apply_rules
