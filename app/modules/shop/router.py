from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.identity.models import User
from app.modules.shop.models import InventoryItem, ShopItem

router = APIRouter(prefix="/shop", tags=["shop"])


class PurchaseRequest(BaseModel):
    user_id: int


@router.get("/items")
def list_items(db: Session = Depends(get_db)) -> list[dict]:
    items = db.scalars(select(ShopItem).where(ShopItem.active.is_(True)).order_by(ShopItem.id)).all()
    return [{"id": item.id, "name": item.name, "item_type": item.item_type, "price": item.price} for item in items]


@router.post("/items/{item_id}/purchase")
def purchase_item(item_id: int, payload: PurchaseRequest, db: Session = Depends(get_db)) -> dict:
    item = db.get(ShopItem, item_id)
    if item is None or not item.active:
        raise HTTPException(status_code=404, detail="item not found")

    spent_user_id = db.scalar(
        update(User)
        .where(User.id == payload.user_id, User.balance >= item.price)
        .values(balance=User.balance - item.price)
        .returning(User.id)
    )
    if spent_user_id is None:
        if db.get(User, payload.user_id) is None:
            raise HTTPException(status_code=404, detail="user not found")
        raise HTTPException(status_code=409, detail="insufficient balance")

    inventory = db.scalar(
        select(InventoryItem)
        .where(InventoryItem.user_id == payload.user_id, InventoryItem.item_id == item.id)
        .with_for_update()
    )
    if inventory is None:
        inventory = InventoryItem(user_id=payload.user_id, item_id=item.id, quantity=1)
        db.add(inventory)
    else:
        inventory.quantity += 1
    db.commit()
    db.refresh(inventory)
    user = db.get(User, payload.user_id)
    return {"item_id": item.id, "quantity": inventory.quantity, "balance": user.balance}
