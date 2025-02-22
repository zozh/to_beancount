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

    config, log_obj, root_path = init_app()
    bean_path = config["paths"]["bean_path"]
    temp_format = config["paths"]["temp_format"]

    account_mapper_type = "wechat"
    if account_mapper_type == "wechat":
        wechatRule = config["rules"]["wechat"]

        account_mapper = AccountMapper(
            target_file=target_file,
            mapping_file=wechatRule["mapping_file"],
            output_file=temp_format,
            match_columns=wechatRule["match_columns"],
        )
        account_mapper.process_transactions()

    beancount_mapper = BeancountMapper(temp_format)
    transactions = beancount_mapper.map_to_transactions()

    beancount_helper = BeancountHelper(bean_path, log_obj, temp_format)
    beancount_helper.write_transaction_list(transactions)
