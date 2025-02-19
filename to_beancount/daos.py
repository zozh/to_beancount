from typing import Optional, List
from sqlalchemy.orm import Session
from models import Hierarchy, Category, HierarchyCategory


class HierarchyDAO:
    def __init__(self, db: Session):
        self.db = db

    def create_hierarchy(self, name: str, parent_id: Optional[int] = None) -> Hierarchy:
        """
        创建一个新的层级对象。
        """
        db_hierarchy = Hierarchy(name=name, parent_id=parent_id)
        self.db.add(db_hierarchy)
        self.db.commit()
        self.db.refresh(db_hierarchy)
        return db_hierarchy

    def get_hierarchy(self, hierarchy_id: int) -> Optional[Hierarchy]:
        """
        根据层级 ID 获取层级对象。
        """
        return self.db.query(Hierarchy).filter(Hierarchy.id == hierarchy_id).first()

    def get_all_hierarchies(self) -> List[Hierarchy]:
        """
        获取所有层级对象。
        """
        return self.db.query(Hierarchy).all()

    def update_hierarchy(self, hierarchy_id: int, name: str) -> Optional[Hierarchy]:
        """
        更新层级对象的名称。
        """
        db_hierarchy = (
            self.db.query(Hierarchy).filter(Hierarchy.id == hierarchy_id).first()
        )
        if db_hierarchy:
            db_hierarchy.name = name
            self.db.commit()
            self.db.refresh(db_hierarchy)
        return db_hierarchy

    def delete_hierarchy(self, hierarchy_id: int) -> None:
        """
        根据层级 ID 删除层级对象。
        """
        db_hierarchy = (
            self.db.query(Hierarchy).filter(Hierarchy.id == hierarchy_id).first()
        )
        if db_hierarchy:
            self.db.delete(db_hierarchy)
            self.db.commit()


class CategoryDAO:
    def __init__(self, db: Session):
        self.db = db

    def create_category(self, name: str, description: str = None) -> Category:
        """
        创建一个新的分类。
        """
        new_category = Category(name=name, description=description)
        self.db.add(new_category)
        self.db.commit()
        self.db.refresh(new_category)
        return new_category

    def get_category(self, category_id: int) -> Optional[Category]:
        """
        根据分类 ID 获取分类详情。
        """
        return self.db.query(Category).filter(Category.id == category_id).first()

    def get_all_categories(self) -> List[Category]:
        """
        获取所有分类。
        """
        return self.db.query(Category).all()

    def update_category(
        self, category_id: int, name: str, description: str
    ) -> Optional[Category]:
        """
        更新分类信息。
        """
        db_category = self.db.query(Category).filter(Category.id == category_id).first()
        if db_category:
            db_category.name = name
            db_category.description = description
            self.db.commit()
            self.db.refresh(db_category)
        return db_category

    def delete_category(self, category_id: int) -> None:
        """
        删除分类。
        """
        db_category = self.db.query(Category).filter(Category.id == category_id).first()
        if db_category:
            self.db.delete(db_category)
            self.db.commit()


class HierarchyCategoryDAO:
    def __init__(self, db: Session):
        self.db = db

    def add_hierarchy_category(self, hierarchy_id: int, category_id: int) -> None:
        """
        添加层级与分类的关联。
        """
        new_association = HierarchyCategory(
            hierarchy_id=hierarchy_id, category_id=category_id
        )
        self.db.add(new_association)
        self.db.commit()

    def remove_hierarchy_category(self, hierarchy_id: int, category_id: int) -> None:
        """
        移除层级与分类的关联。
        """
        db_association = (
            self.db.query(HierarchyCategory)
            .filter(
                HierarchyCategory.hierarchy_id == hierarchy_id,
                HierarchyCategory.category_id == category_id,
            )
            .first()
        )
        if db_association:
            self.db.delete(db_association)
            self.db.commit()

    def get_categories_by_hierarchy(self, hierarchy_id: int) -> List[Category]:
        """
        根据层级 ID 获取关联的分类。
        """
        hierarchy_categories = (
            self.db.query(HierarchyCategory)
            .filter(HierarchyCategory.hierarchy_id == hierarchy_id)
            .all()
        )
        category_ids = [hc.category_id for hc in hierarchy_categories]
        return self.db.query(Category).filter(Category.id.in_(category_ids)).all()

    def get_hierarchies_by_category(self, category_id: int) -> List[Hierarchy]:
        """
        根据分类 ID 获取关联的层级。
        """
        category_hierarchies = (
            self.db.query(HierarchyCategory)
            .filter(HierarchyCategory.category_id == category_id)
            .all()
        )
        hierarchy_ids = [hc.hierarchy_id for hc in category_hierarchies]
        return self.db.query(Hierarchy).filter(Hierarchy.id.in_(hierarchy_ids)).all()
