import os
from pathlib import Path
from typing import List


class SingletonMeta(type):
    """
    单例模式的元类实现。

    该元类确保所有使用它的类只会有一个实例。
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        调用类时触发的方法。

        如果类的实例已经存在，则直接返回该实例；
        否则，创建一个新的实例并保存。

        Args:
            cls (type): 当前类。
            *args: 可变参数，传递给类的构造函数。
            **kwargs: 关键字参数，传递给类的构造函数。

        Returns:
            object: 类的唯一实例。
        """
        if cls not in cls._instances:
            # 如果类还没有实例化，则创建一个实例并保存
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AppDataPath(metaclass=SingletonMeta):
    """
    应用程序数据路径管理类。

    根据应用名初始化本地应用程序数据目录，并创建指定的子目录结构。
    """

    def __init__(self, app_name: str, subdirectory: List[str]):
        """
        初始化应用程序数据路径。

        Args:
            app_name (str): 应用程序名称，用于生成数据目录。
        """
        self.app_name = app_name
        # 获取本地应用程序数据目录
        local_app_data = Path(os.getenv("LOCALAPPDATA", ""))
        self.base_path = local_app_data / self.app_name / "data"
        self.subdirectory = subdirectory

        # 创建基础目录及子目录
        self._create_directories()

    def _create_directories(self):
        """
        创建基础目录和所有子目录。
        """
        self.base_path.mkdir(parents=True, exist_ok=True)
        for subdir in self.subdirectory:
            (self.base_path / subdir).mkdir(exist_ok=True)

    def __repr__(self):
        return f"AppDataPath(app_name='{self.app_name}', base_path='{self.base_path}')"

    def get_path(self, subdirectory: str = "") -> Path:
        """
        获取指定子目录的完整路径。

        Args:
            subdirectory (str): 子目录名称（可选）。如果为空，则返回基础目录。

        Returns:
            Path: 指定子目录的路径。
        """
        if subdirectory and subdirectory in self.subdirectory:
            return self.base_path / subdirectory
        return self.base_path

    def get_absolute_path(self, relative_path: str) -> Path:
        """
        将相对路径转换为绝对路径。

        Args:
            relative_path (str): 相对路径。

        Returns:
            Path: 绝对路径。
        """
        # 确保相对路径是以 "data/" 开头
        if not relative_path.startswith("data/"):
            raise ValueError("相对路径必须以 'data/' 开头")

        # 去掉 "data/" 前缀，拼接基础路径
        sub_path = Path(relative_path[len("data/") :])
        return self.base_path / sub_path
