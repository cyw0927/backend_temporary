from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.modules.economy.models import RewardLedger
from app.modules.grading import service as grading_service
from app.modules.grading.models import Attempt
from app.modules.housing.models import HousingPlacement
from app.modules.identity.models import User
from app.modules.identity.service import UserNotFoundError, lookup_user
from app.modules.learning.models import LearningTask
from app.modules.shop.models import InventoryItem, ShopItem


def make_test_context():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    Base.metadata.create_all(engine)

    app = create_app()

    def override_get_db():
        with TestingSessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    grading_service.SessionLocal = TestingSessionLocal
    return TestClient(app), TestingSessionLocal


def seed(db: Session) -> tuple[User, LearningTask, ShopItem]:
    user = User(
        username="tester",
        role="USER",
        balance=20,
        mileage=0,
        house_level=1,
        wallpaper_item_id=None,
        floor_item_id=None,
    )
    task = LearningTask(
        title="hello",
        description="print hello",
        starter_code="",
        reference_solution='print("hello")',
        reward_amount=7,
    )
    item = ShopItem(name="chair", item_type="furniture", price=10, active=True)
    db.add_all([user, task, item])
    db.commit()
    db.refresh(user)
    db.refresh(task)
    db.refresh(item)
    return user, task, item


def test_user_lookup_service_is_database_independent() -> None:
    user = User(
        id=42,
        username="service-test",
        role="USER",
        balance=0,
        mileage=0,
        house_level=1,
        wallpaper_item_id=None,
        floor_item_id=None,
    )
    assert lookup_user(42, lambda user_id: user if user_id == 42 else None) is user

    try:
        lookup_user(404, lambda _user_id: None)
    except UserNotFoundError as exc:
        assert exc.args == (404,)
    else:
        raise AssertionError("missing user must raise UserNotFoundError")


def test_health_user_and_task_listing():
    client, SessionLocal = make_test_context()
    with SessionLocal() as db:
        user, task, _ = seed(db)
        user_id, task_id = user.id, task.id

    assert client.get("/health").json() == {"status": "ok"}
    assert client.get(f"/users/{user_id}").status_code == 200
    tasks = client.get("/tasks")
    assert tasks.status_code == 200
    assert tasks.json()[0]["id"] == task_id
    assert "reference_solution" not in tasks.json()[0]
    detail = client.get(f"/tasks/{task_id}")
    assert detail.status_code == 200
    assert detail.json()["id"] == task_id

    shop_items = client.get("/shop/items")
    assert shop_items.status_code == 200
    assert shop_items.json()[0]["item_type"] == "furniture"


def test_submit_poll_and_reward_is_idempotent():
    client, SessionLocal = make_test_context()
    with SessionLocal() as db:
        user, task, _ = seed(db)
        user_id, task_id = user.id, task.id

    response = client.post(
        f"/tasks/{task_id}/submissions",
        json={"user_id": user_id, "code": 'print("hello")'},
    )
    assert response.status_code == 202
    assert response.json()["status"] == "PENDING"
    attempt_id = response.json()["attempt_id"]

    polled = client.get(f"/attempts/{attempt_id}")
    assert polled.status_code == 200
    assert polled.json()["status"] == "COMPLETED"
    assert polled.json()["is_correct"] is True

    with SessionLocal() as db:
        user = db.get(User, user_id)
        assert user.balance == 27
        assert db.scalar(select(RewardLedger).where(RewardLedger.attempt_id == attempt_id)) is not None

    grading_service.grade_attempt(attempt_id)
    with SessionLocal() as db:
        assert db.get(User, user_id).balance == 27
        assert len(db.scalars(select(RewardLedger)).all()) == 1


def test_shop_purchase_insufficient_and_success_then_housing():
    client, SessionLocal = make_test_context()
    with SessionLocal() as db:
        user, _, item = seed(db)
        user_id, item_id = user.id, item.id

    insufficient = client.post(f"/shop/items/{item_id}/purchase", json={"user_id": user_id + 999})
    assert insufficient.status_code == 404

    with SessionLocal() as db:
        poor = User(
            username="poor",
            role="USER",
            balance=5,
            mileage=0,
            house_level=1,
            wallpaper_item_id=None,
            floor_item_id=None,
        )
        db.add(poor)
        db.commit()
        db.refresh(poor)
        poor_id = poor.id

    insufficient = client.post(f"/shop/items/{item_id}/purchase", json={"user_id": poor_id})
    assert insufficient.status_code == 409

    bought = client.post(f"/shop/items/{item_id}/purchase", json={"user_id": user_id})
    assert bought.status_code == 200
    assert bought.json()["balance"] == 10
    assert bought.json()["quantity"] == 1

    housing = client.get(f"/users/{user_id}/housing")
    assert housing.status_code == 200
    assert housing.json()["owned_items"][0]["item_id"] == item_id

    equipped = client.put(f"/users/{user_id}/housing/main", json={"item_id": item_id})
    assert equipped.status_code == 200

    with SessionLocal() as db:
        inventory = db.scalar(select(InventoryItem).where(InventoryItem.user_id == user_id))
        placement = db.scalar(select(HousingPlacement).where(HousingPlacement.user_id == user_id))
        assert inventory.quantity == 1
        assert placement.item_id == item_id


def test_housing_rejects_unowned_item():
    client, SessionLocal = make_test_context()
    with SessionLocal() as db:
        user, _, item = seed(db)
        user_id, item_id = user.id, item.id

    response = client.put(f"/users/{user_id}/housing/main", json={"item_id": item_id})
    assert response.status_code == 403
