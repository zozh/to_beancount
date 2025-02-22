from datetime import datetime
import random

temp_format = (
    f"{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}_{str(random.randint(1000, 9999))}"
)

configs = {
    "app": {
        "name": "beancount_helper",
        "data_subdirectory": ["bean", "rule", "logs", "temp"],
        "bean_path": "data/bean/moneybook.bean",
        "out_bean": f"data/bean/{temp_format}.bean",
        "temp_csv": f"data/temp/{temp_format}.csv",
        "log": {
            "path": "data/logs",
            "level": "DEBUG",
            "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red",
            },
        },
    },
    "rules": {
        "wechat": {
            "mapping_file": "data/rule/wechat_rule.xlsx",
            "match_columns": {
                "expenses": {
                    "columns": ["交易类型", "交易对方", "商品"],
                    "default": "Expenses:Node",
                },
                "assets": {"columns": ["支付方式"], "default": "Assets:Node"},
            },
        },
        "alipay": {
            "mapping_file": "data/rule/alipay_rule.xlsx",
            "match_columns": {
                "expenses": {
                    "columns": ["交易分类", "交易对方", "商品说明"],
                    "default": "Expenses:Node",
                },
                "assets": {"columns": ["收/付款方式"], "default": "Assets:Node"},
            },
        },
    },
}
