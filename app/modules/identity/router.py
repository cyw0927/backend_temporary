from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.identity.models import User
from app.modules.identity.service import UserNotFoundError, lookup_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        user = lookup_user(user_id, lambda requested_id: db.get(User, requested_id))
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="user not found")
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "balance": user.balance,
        "mileage": user.mileage,
        "house_level": user.house_level,
        "wallpaper_item_id": user.wallpaper_item_id,
        "floor_item_id": user.floor_item_id,
    }
