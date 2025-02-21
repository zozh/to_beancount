#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename : strategy.py
@Author : ZouZhao
@Contact : wszwc3721@163.com
@Time : 2025/01/17 20:41
@License : Copyright (c) 2025 by ZouZhao, All Rights Reserved.
@Description : 策略
"""

__copyright__ = "Copyright (c) 2025 by ZouZhao, All Rights Reserved."
__license__ = None

# strategy.py
from abc import ABC, abstractmethod
from typing import Dict, List, NoReturn

from beancount_tool import Transaction
import pandas as pd
from pipeline import (
    to_data,
    to_amount,
    to_remark,
    to_status,
    to_description,
    to_currency,
    apply_rules,
)


class ParsingStrategy(ABC):
    """解析基类"""

    def __init__(self, rule, csv_path: str) -> NoReturn:
        """初始化"""
        self._rule = rule
        self._csv_path = csv_path
        self._transaction_list = []
        self._pipeline = []
        self._df = pd.read_csv(csv_path)
        self.read_csv()
        self._csv_clean()
        self._build_pipeline()

    @abstractmethod
    def _csv_clean(self) -> NoReturn:
        """数据清洗"""
        pass

    @abstractmethod
    def _build_pipeline(self) -> NoReturn:
        """构建数据处理管道"""
        pass

    def read_csv(self) -> NoReturn:
        pass

    def _run_pipeline(self, data: Dict) -> Dict:
        """运行数据处理管道"""
        for func in self._pipeline:
            data = func(data)
        return data

    def csv_to_transaction(self) -> List[Transaction]:
        """csv 转化 transaction"""
        for _, row in self._df.iterrows():
            row_dict = row.to_dict()
            result = self._run_pipeline(row_dict)
            transaction = Transaction.from_dict(result)
            self._transaction_list.append(transaction)
        return self._transaction_list


class StrategyFactory:
    """策略类工厂"""

    @staticmethod
    def get_strategy(strategy_type: str, rule: dict, csv_path: str) -> ParsingStrategy:
        """
        根据策略类型和参数创建相应的策略实例。

        Args:
            strategy_type (str): 策略类型，例如 "wechat" 或 "alipay"。
            params (dict): 策略初始化所需的参数字典。

        Returns:
            ParsingStrategy: 创建的策略实例。

        Raises:
            ValueError: 如果策略类型未知。
        """
        if strategy_type == "wechat":
            return WechatParsingStrategy(rule, csv_path)
        elif strategy_type == "alipay":
            return AlipayParsingStrategy(rule, csv_path)
        else:
            raise ValueError("Unknown strategy type")


class AlipayParsingStrategy(ParsingStrategy):
    """支付宝解析类"""

    def _csv_clean(self) -> NoReturn:
        """数据清洗"""
        pass

    def _build_pipeline(self) -> NoReturn:
        self._pipeline = [
            to_data("交易时间", "%Y-%m-%d %H:%M:%S"),
            to_amount("金额"),
            to_remark(["交易对方", "备注"]),
            to_status("*"),
            to_description("交易对方"),
            to_currency("CNY"),
            apply_rules(self._rule),
        ]


class WechatParsingStrategy(ParsingStrategy):
    """微信解析类"""

    def _csv_clean(self) -> NoReturn:
        """数据清洗"""
        pass

    def _build_pipeline(self) -> NoReturn:
        self._pipeline = [
            to_data("交易时间", "%Y/%m/%d %H:%M"),
            to_amount("金额(元)"),
            to_remark(["交易对方", "备注"]),
            to_status("*"),
            to_description("交易对方"),
            to_currency("CNY"),
            apply_rules(self._rule),
        ]
