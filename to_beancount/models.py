from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


# 初始化数据库
Base = declarative_base()


# 定义 Hierarchy 模型
class Hierarchy(Base):
    __tablename__ = "hierarchy"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    parent_id = Column(Integer, ForeignKey("hierarchy.id"))


# 定义 Category 模型
class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)


# 定义关联表 HierarchyCategory
class HierarchyCategory(Base):
    __tablename__ = "hierarchy_category"
    hierarchy_id = Column(Integer, ForeignKey("hierarchy.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("category.id"), primary_key=True)


class DatabaseManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        Base.metadata.create_all(bind=self.engine, checkfirst=True)

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # 如果发生异常，回滚事务
            self.session.rollback()
        else:
            # 没有异常，提交事务
            self.session.commit()
        # 关闭会话
        self.session.close()

    def get_session(self) -> Session:
        """返回数据库操作的SQLAlchemy Session实例。
        Returns:
            Session:用于与数据库交互的Session对象。
        """
        return self.session
