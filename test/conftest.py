import os
import sys
from dotenv import load_dotenv


def path_under_test():
    load_dotenv()
    test_pkg_path = os.getenv("PATH_UNDER_TEST")
    print(test_pkg_path)
    if test_pkg_path:
        sys.path.append(test_pkg_path)
        print(sys.path)
    else:
        raise ValueError("环境变量 TEST_PKG_PATH 未设置，请配置该变量。")


path_under_test()
