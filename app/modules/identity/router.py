from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.identity.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)) -> dict:
    user = db.get(User, user_id)
    if user is None:
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
