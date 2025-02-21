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
from typing import NoReturn


class AccountMapper:
    def __init__(
        self, target_file: str, mapping_file: str, output_file: str, match_columns: dict
    ) -> NoReturn:
        """初始化 TransactionMapper 类。
        Args:
            target_file (str): 目标文件路径（CSV）。
            mapping_file (str): 映射文件路径（Excel）。
            output_file (str): 输出文件路径（CSV）。
            match_columns (dict): 匹配列的字典，包含匹配列和默认值。
        Returns:
            NoReturn
        """
        self.target_file = target_file
        self.mapping_file = mapping_file
        self.output_file = output_file
        self.match_columns = match_columns

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
            if pd.notna(mapping_row[col]):  # 如果映射表中的该项不为空
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

        # 将默认值转换为长度为 2 的元组
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

        # 返回默认值
        return default_value

    def process_transactions(self) -> NoReturn:
        """处理交易数据并保存结果。
        Returns:
            NoReturn
        """
        # 读取目标表（CSV）
        target_df = pd.read_csv(self.target_file, skiprows=16, encoding="utf8")

        # 读取映射关系表（Excel）
        expenses_mapping = pd.read_excel(self.mapping_file, sheet_name="Expenses")
        assets_mapping = pd.read_excel(self.mapping_file, sheet_name="Assets")

        # 初始化结果列
        target_df["debit_id"] = None
        target_df["debit"] = None
        target_df["credit_id"] = None
        target_df["credit"] = None

        # 遍历每笔交易
        for index, transaction in target_df.iterrows():
            # 映射Expenses
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


if __name__ == "__main__":
    # 创建TransactionMapper实例并处理交易数据
    mapper = AccountMapper(
        target_file=r"data\bill\微信支付账单(20250101-20250221).csv",
        mapping_file=r"data\wechat_rule.xlsx",
        output_file=r"mapped_target.csv",
        match_columns={
            "expenses": {
                "columns": ["交易类型", "交易对方", "商品"],
                "default": "Expenses:Node",
            },
            "assets": {
                "columns": ["支付方式"],
                "default": "Assets:Node",
            },
        },
    )
    mapper.process_transactions()
