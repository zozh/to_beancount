#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename : mapper.py
@Author : ZouZhao
@Contact : wszwc3721@163.com
@Time : 2025/02/21 21:34
@License : Copyright (c) 2025 by ZouZhao, All Rights Reserved.
@Description : 映射
"""

__copyright__ = "Copyright (c) 2025 by ZouZhao, All Rights Reserved."
__license__ = None

import pandas as pd
from typing import NoReturn, List, Dict
from conversion import Transaction
from pipeline import (
    to_data,
    to_amount,
    to_remark,
    to_status,
    to_description,
    to_currency,
)


class AccountMapper:
    def __init__(
        self,
        target_file: str,
        map: dict,
        output_file: str,
    ) -> NoReturn:
        """初始化 TransactionMapper 类。

        Args:
            target_file (str): 目标文件路径（CSV）。
            map (dict): 映射规则字典。
            output_file (str): 输出文件路径（CSV）。
        Returns:

            NoReturn
        """
        self.target_file = target_file
        self.mapping_file = map["mapping_file"]
        self.output_file = output_file
        self.match_columns = map["match_columns"]

    def generate_mask(
        self, mapping_row: pd.Series, transaction: pd.Series, columns: list
    ) -> bool:
        """生成匹配条件的辅助函数。

        Args:
            mapping_row (pd.Series): 映射表中的一行数据。
            transaction (pd.Series): 交易数据。
            columns (list): 匹配列。
        Returns:

            bool: 是否满足匹配条件。
        """
        conditions = []
        for col in columns:
            if pd.notna(mapping_row[col]):
                conditions.append(mapping_row[col] == transaction[col])
        return all(conditions) if conditions else False

    def map_generic(
        self, transaction: pd.Series, mapping_table: pd.DataFrame, mapping_type: str
    ) -> tuple:
        """通用匹配方法，用于匹配费用或资产信息。

        Args:
            transaction (pd.Series): 交易数据。
            mapping_table (pd.DataFrame): 映射表。
            mapping_type (str): 匹配类型（如 "expenses" 或 "assets"）。

        Returns:
            tuple: 匹配结果（编号和值），如果未匹配则返回默认值。
        """
        match_info = self.match_columns.get(mapping_type, {})
        match_columns = match_info.get("columns", [])
        default_value = match_info.get("default", None)

        if isinstance(default_value, str):
            default_value = (None, default_value)

        if not match_columns or default_value is None:
            return (None, None)

        if mapping_type == "assets":
            mask = mapping_table[match_columns[0]] == transaction[match_columns[0]]
            matching_rows = mapping_table[mask]
            if not matching_rows.empty:
                return matching_rows.iloc[0]["编号"], matching_rows.iloc[0]["值"]

        elif mapping_type == "expenses":
            for _, mapping_row in mapping_table.iterrows():
                if self.generate_mask(mapping_row, transaction, match_columns):
                    return mapping_row["编号"], mapping_row["值"]

        return default_value

    def process_transactions(self) -> NoReturn:
        """处理交易数据并保存结果。

        Returns:
            NoReturn
        """
        target_df = pd.read_csv(self.target_file, skiprows=16, encoding="utf8")

        expenses_mapping = pd.read_excel(self.mapping_file, sheet_name="Expenses")
        assets_mapping = pd.read_excel(self.mapping_file, sheet_name="Assets")

        target_df["debit_id"] = None
        target_df["debit"] = None
        target_df["credit_id"] = None
        target_df["credit"] = None

        for index, transaction in target_df.iterrows():

            debit_id, debit = self.map_generic(
                transaction, expenses_mapping, "expenses"
            )
            credit_id, credit = self.map_generic(transaction, assets_mapping, "assets")

            if target_df.loc[index, "收/支"] == "收入":
                target_df.loc[index, ["debit_id", "debit"]] = [credit_id, credit]
                target_df.loc[index, ["credit_id", "credit"]] = [debit_id, debit]
                target_df.to_csv(self.output_file, index=False, encoding="gb18030")
                continue

            target_df.loc[index, ["debit_id", "debit"]] = [debit_id, debit]
            target_df.loc[index, ["credit_id", "credit"]] = [credit_id, credit]
            target_df.to_csv(self.output_file, index=False, encoding="gb18030")


class BeancountMapper:
    """Beancount 映射器，用于将目标表数据映射为 Transaction 对象"""

    def __init__(self, target_file: str) -> NoReturn:
        """
        初始化 BeancountMapper。

        Args:
            rule (dict): 匹配规则。
        """
        self.df = pd.read_csv(target_file, encoding="gb18030")

    def map_to_transactions(self) -> List[Transaction]:
        """
        将 DataFrame 中的数据映射为 Transaction 字典列表。

        Args:
            df (pd.DataFrame): 输入的目标表数据。

        Returns:
            List[Dict]: 映射后的 Transaction 字典列表。
        """
        transactions = []
        for _, row in self.df.iterrows():
            transaction = self._map_row_to_transaction(row)
            if transaction:
                transactions.append(Transaction.from_dict(transaction))
        return transactions

    def _map_row_to_transaction(self, row: pd.Series) -> Dict:
        """
        将单行数据映射为 Transaction 字典。

        Args:
            row (pd.Series): 单行数据。

        Returns:
            Dict: 映射后的 Transaction 字典。
        """
        pipelines = [
            to_data("交易时间", "%Y-%m-%d %H:%M:%S"),
            to_amount("金额(元)"),
            to_remark(["备注", "交易单号"], "wechat"),
            to_status("*"),
            to_description("交易对方"),
            to_currency("CNY"),
        ]

        data = row.to_dict()
        for func in pipelines:
            data = func(data)

        if not all(
            key in data
            for key in [
                "date",
                "status",
                "description",
                "amount",
                "currency",
                "remark",
                "debit",
                "credit",
            ]
        ):
            return None
        return data
