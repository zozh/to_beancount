import logging


class Rule:
    output_file = r"mapped_target.csv"


class wechatRule(Rule):
    mapping_file = r"data\wechat_rule.xlsx"
    match_columns = (
        {
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


class alipayRule(Rule):
    mapping_file = r"data\alipay_rule.xlsx"
    match_columns = (
        {
            "expenses": {
                "columns": ["交易分类", "交易对方", "商品说明"],
                "default": "Expenses:Node",
            },
            "assets": {
                "columns": ["收/付款方式"],
                "default": "Assets:Node",
            },
        },
    )


class Config:
    app_name = "beancount_helper"
    log_path = "logs"
    log_level = logging.DEBUG
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_datefmt = "%Y-%m-%d %H:%M:%S"
    log_colors = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red",
    }
