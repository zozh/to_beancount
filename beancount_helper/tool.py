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
