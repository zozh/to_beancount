from strategy import StrategyFactory
from mapper import load_yaml, build_tree_from_yaml
from log import SingletonLogger

if __name__ == "__main__":

    singleton_logger = SingletonLogger()
    logger = singleton_logger.get_logger()

    rule = r"data\rule.yaml"
    yaml_data = load_yaml(r"try\rules.yaml")
    rule_tree = build_tree_from_yaml(yaml_data, logger)

    csv_path = r"data\bill\微信支付账单(20240809-20241109).csv"
    strategy = StrategyFactory.get_strategy("wechat", rule_tree, csv_path)

    for item in strategy.csv_to_transaction():
        print(item)
