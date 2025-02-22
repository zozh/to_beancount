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


from mapper import AccountMapper, BeancountMapper
from beancount_tool import BeancountHelper
from init import init_app


if __name__ == "__main__":
    target_file = r"try\bill\微信支付账单(20250101-20250221).csv"

    app_config, rules, log_obj = init_app()
    bean_path = app_config["bean_path"]
    temp_csv_path = app_config["temp_csv"]
    out_bean_path = app_config["out_bean"]

    account_type = "wechat"
    if account_type == "wechat":
        wechatRule = rules["wechat"]

        account_mapper = AccountMapper(
            target_file=target_file,
            map=wechatRule,
            output_file=temp_csv_path,
        )
        account_mapper.process_transactions()

    # 转化后为 beancount
    beancount_mapper = BeancountMapper(temp_csv_path)
    transactions = beancount_mapper.map_to_transactions()
    beancount_helper = BeancountHelper(bean_path, out_bean_path, log_obj)
    beancount_helper.write_transaction_list(transactions)
