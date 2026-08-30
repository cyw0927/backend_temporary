from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.housing.models import HousingPlacement
from app.modules.identity.models import User
from app.modules.shop.models import InventoryItem, ShopItem

router = APIRouter(prefix="/users/{user_id}/housing", tags=["housing"])


class EquipRequest(BaseModel):
    item_id: int


@router.get("")
def get_housing(user_id: int, db: Session = Depends(get_db)) -> dict:
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="user not found")
    owned_rows = db.execute(
        select(InventoryItem, ShopItem)
        .join(ShopItem, ShopItem.id == InventoryItem.item_id)
        .where(InventoryItem.user_id == user_id)
        .order_by(InventoryItem.id)
    ).all()
    placements = db.scalars(
        select(HousingPlacement).where(HousingPlacement.user_id == user_id).order_by(HousingPlacement.slot)
    ).all()
    return {
        "owned_items": [
            {"item_id": inv.item_id, "name": item.name, "item_type": item.item_type, "quantity": inv.quantity}
            for inv, item in owned_rows
        ],
        "placements": [{"slot": row.slot, "item_id": row.item_id} for row in placements],
    }


@router.put("/{slot}")
def equip_item(user_id: int, slot: str, payload: EquipRequest, db: Session = Depends(get_db)) -> dict:
    owned = db.scalar(
        select(InventoryItem).where(
            InventoryItem.user_id == user_id,
            InventoryItem.item_id == payload.item_id,
            InventoryItem.quantity > 0,
        )
    )
    item = db.get(ShopItem, payload.item_id)
    if owned is None or item is None:
        raise HTTPException(status_code=403, detail="item is not owned")
    if item.item_type != "furniture":
        raise HTTPException(status_code=409, detail="item is not furniture")

    placement = db.scalar(
        select(HousingPlacement)
        .where(HousingPlacement.user_id == user_id, HousingPlacement.slot == slot)
        .with_for_update()
    )
    if placement is None:
        placement = HousingPlacement(user_id=user_id, item_id=item.id, slot=slot)
        db.add(placement)
    else:
        placement.item_id = item.id
    db.commit()
    return {"slot": slot, "item_id": item.id}
