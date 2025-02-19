import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from to_beancount.models import Hierarchy, Category, HierarchyCategory
from to_beancount.daos import HierarchyDAO, CategoryDAO, HierarchyCategoryDAO


@pytest.fixture
def setup_db():
    # 初始化数据库连接和会话
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    db = Session()

    # 创建所有表
    Hierarchy.__table__.create(engine)
    Category.__table__.create(engine)
    HierarchyCategory.__table__.create(engine)
    yield db
    # 清理数据库
    Hierarchy.__table__.drop(engine)
    Category.__table__.drop(engine)
    HierarchyCategory.__table__.drop(engine)


@pytest.fixture
def hierarchy_dao(setup_db):
    return HierarchyDAO(setup_db)


@pytest.fixture
def category_dao(setup_db):
    return CategoryDAO(setup_db)


@pytest.fixture
def hierarchy_category_dao(setup_db):
    return HierarchyCategoryDAO(setup_db)


def test_create_hierarchy(hierarchy_dao):
    # 测试创建层级
    hierarchy = hierarchy_dao.create_hierarchy("Test Hierarchy")
    assert hierarchy is not None
    assert hierarchy.name == "Test Hierarchy"


def test_get_hierarchy(hierarchy_dao):
    # 创建一个层级
    hierarchy = hierarchy_dao.create_hierarchy("Test Hierarchy")
    # 测试获取层级
    retrieved = hierarchy_dao.get_hierarchy(hierarchy.id)
    assert retrieved is not None
    assert retrieved.id == hierarchy.id


def test_get_all_hierarchies(hierarchy_dao):
    # 创建多个层级
    hierarchy_dao.create_hierarchy("H1")
    hierarchy_dao.create_hierarchy("H2")
    # 测试获取所有层级
    hierarchies = hierarchy_dao.get_all_hierarchies()
    assert len(hierarchies) == 2


def test_update_hierarchy(hierarchy_dao):
    # 创建一个层级
    hierarchy = hierarchy_dao.create_hierarchy("Old Name")
    # 更新层级名称
    updated = hierarchy_dao.update_hierarchy(hierarchy.id, "New Name")
    assert updated is not None
    assert updated.name == "New Name"


def test_delete_hierarchy(hierarchy_dao):
    # 创建一个层级
    hierarchy = hierarchy_dao.create_hierarchy("Test Hierarchy")
    # 删除层级
    hierarchy_dao.delete_hierarchy(hierarchy.id)
    # 验证删除
    assert hierarchy_dao.get_hierarchy(hierarchy.id) is None


def test_create_category(category_dao):
    # 测试创建分类
    category = category_dao.create_category("Test Category")
    assert category is not None
    assert category.name == "Test Category"


def test_get_category(category_dao):
    # 创建一个分类
    category = category_dao.create_category("Test Category")
    # 测试获取分类
    retrieved = category_dao.get_category(category.id)
    assert retrieved is not None
    assert retrieved.id == category.id


def test_get_all_categories(category_dao):
    # 创建多个分类
    category_dao.create_category("C1")
    category_dao.create_category("C2")
    # 测试获取所有分类
    categories = category_dao.get_all_categories()
    assert len(categories) == 2


def test_update_category(category_dao):
    # 创建一个分类
    category = category_dao.create_category("Old Name", "Old Description")
    # 更新分类
    updated = category_dao.update_category(category.id, "New Name", "New Description")
    assert updated is not None
    assert updated.name == "New Name"


def test_delete_category(category_dao):
    # 创建一个分类
    category = category_dao.create_category("Test Category")
    # 删除分类
    category_dao.delete_category(category.id)
    # 验证删除
    assert category_dao.get_category(category.id) is None


def test_add_hierarchy_category(hierarchy_category_dao, hierarchy_dao, category_dao):
    # 创建层级和分类
    hierarchy = hierarchy_dao.create_hierarchy("Test Hierarchy")
    category = category_dao.create_category("Test Category")
    # 添加关联
    hierarchy_category_dao.add_hierarchy_category(hierarchy.id, category.id)
    # 验证关联存在
    relevance = (
        hierarchy_category_dao.db.query(HierarchyCategory)
        .filter(
            HierarchyCategory.hierarchy_id == hierarchy.id,
            HierarchyCategory.category_id == category.id,
        )
        .first()
    )
    assert relevance is not None


def test_remove_hierarchy_category(hierarchy_category_dao, hierarchy_dao, category_dao):
    # 创建层级和分类
    hierarchy = hierarchy_dao.create_hierarchy("Test Hierarchy")
    category = category_dao.create_category("Test Category")
    # 添加关联
    hierarchy_category_dao.add_hierarchy_category(hierarchy.id, category.id)
    # 移除关联
    hierarchy_category_dao.remove_hierarchy_category(hierarchy.id, category.id)
    # 验证关联已删除
    relevance = (
        hierarchy_category_dao.db.query(HierarchyCategory)
        .filter(
            HierarchyCategory.hierarchy_id == hierarchy.id,
            HierarchyCategory.category_id == category.id,
        )
        .first()
    )
    assert relevance is None


def test_get_categories_by_hierarchy(
    hierarchy_category_dao, hierarchy_dao, category_dao
):
    # 创建层级和分类
    hierarchy = hierarchy_dao.create_hierarchy("Test Hierarchy")
    category1 = category_dao.create_category("Category1")
    category2 = category_dao.create_category("Category2")
    # 添加关联
    hierarchy_category_dao.add_hierarchy_category(hierarchy.id, category1.id)
    hierarchy_category_dao.add_hierarchy_category(hierarchy.id, category2.id)
    # 获取分类
    categories = hierarchy_category_dao.get_categories_by_hierarchy(hierarchy.id)
    assert len(categories) == 2
    assert category1 in categories
    assert category2 in categories
