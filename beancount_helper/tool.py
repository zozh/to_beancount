#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename : tool.py
@Author : ZouZhao
@Contact : wszwc3721@163.com
@Time : 2025/02/26 13:22
@License : Copyright (c) 2025 by ZouZhao, All Rights Reserved.
@Description : 工具类
"""

__copyright__ = "Copyright (c) 2025 by ZouZhao, All Rights Reserved."
__license__ = None

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
        local_app_data = Path(os.getenv("LOCALAPPDATA", ""))
        self.base_path = local_app_data / self.app_name / "data"
        self.subdirectory = subdirectory

        self.create_directories()

    def create_directories(self, is_cover: bool = False):
        """
        创建基础目录和所有子目录。

        Args:
            is_cover (bool): 是否覆盖已存在的目录。如果为 True，则删除并重新创建目录；
                            如果为 False，则仅在目录不存在时创建。
        """
        if is_cover and self.base_path.exists():
            self._remove_directory(self.base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        for subdir in self.subdirectory:
            subdir_path = self.base_path / subdir
            subdir_path.mkdir(exist_ok=True)

    def _remove_directory(self, directory: Path):
        """
        递归删除目录及其内容。

        Args:
            directory (Path): 要删除的目录路径。
        """
        if not directory.exists():
            return

        for item in directory.iterdir():
            if item.is_dir():
                self._remove_directory(item)
            else:
                item.unlink()
        directory.rmdir()

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
        if not relative_path.startswith("data/"):
            raise ValueError("相对路径必须以 'data/' 开头")

        sub_path = Path(relative_path[len("data/") :])
        return self.base_path / sub_path
