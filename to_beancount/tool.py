from typing import TypeVar, Callable, Type, Any

T = TypeVar("T")


def singleton(cls: Type[T]) -> Callable[..., T]:
    """
    单例模式装饰器，确保类只有一个实例。

    Args:
        cls (Type[T]): 需要被装饰的类。

    Returns:
        Callable[..., T]: 返回一个函数，该函数用于创建或获取类的单例实例。
    """
    instances = {}

    def get_instance(*args: Any, **kwargs: Any) -> T:
        """
        创建或返回类的单例实例。

        Args:
            *args (Any): 传递给类构造函数的参数。
            **kwargs (Any): 传递给类构造函数的关键字参数。

        Returns:
            T: 类的单例实例。
        """
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


if __name__ == "__main__":
    # 测试
    class Example:
        def __init__(self, name: str):
            self.name = name

        def __repr__(self):
            return f"Example(name={self.name})"

    # 装饰类
    singleton_example = singleton(Example)

    # 创建实例
    instance1 = singleton_example("Instance1")
    # 输出: Example(name=Instance1)
    print(instance1)

    # 尝试创建另一个实例
    instance2 = singleton_example("Instance2")
    # 输出: Example(name=Instance1)
    print(instance2)

    # 测试单例行为
    # 输出: True
    print(instance1 is instance2)
