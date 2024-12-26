from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from ..db.config import get_db
from ..models.app_models import User
from ..utils.logger_handler import logger
from ..routes.auth_router import get_current_user
from ..schemas.user_schema import UserOutSchema, PasswordChangeSchema
from ..utils.password_handler import verify_password, hash_password

user_route = APIRouter(prefix="/api/v1/user", tags=["My user Router"])


@user_route.get("/me", response_model=UserOutSchema, status_code=status.HTTP_200_OK, name="current_user")
async def me(current_user: UserOutSchema = Depends(get_current_user)):
    logger.info(f"Current User Fetched successfully! {current_user.username}")
    return current_user


@user_route.put("/password-update", status_code=status.HTTP_204_NO_CONTENT, name="update_password")
async def update_password(password_update: PasswordChangeSchema, db: Session = Depends(get_db),
                          current_user: UserOutSchema = Depends(get_current_user)):
    if not password_update.new_password == password_update.confirmed_password:
        logger.warning("Passwords do not match!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match!")

    is_user = db.query(User).filter(User.id == current_user.id).first()  # type:ignore

    if not verify_password(password_update.old_password, is_user.password):
        logger.warning("Invalid old password!")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid old password!")

    hashed_password = hash_password(password_update.confirmed_password)

    is_user.password = hashed_password

    db.commit()
    logger.info("Password updated successfully!")


@user_route.put("/set-active", status_code=status.HTTP_204_NO_CONTENT, name="set_active")
async def set_active(db: Session = Depends(get_db), current_user: UserOutSchema = Depends(get_current_user)):
    is_user = db.query(User).filter(User.id == current_user.id).first()  # type:ignore
    if is_user.is_active:
        is_user.is_active = False
    else:
        is_user.is_active = True
    db.commit()
    logger.info(f"User {is_user.username} active status updated successfully!")


@user_route.delete("/remove", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(db: Session = Depends(get_db), current_user: UserOutSchema = Depends(get_current_user)):
    is_user = db.query(User).filter(User.id == current_user.id).first()  # type:ignore
    try:
        db.delete(is_user)
        db.commit()
        logger.info("User removed successfully!")
    except Exception as e:
        logger.error(f"Failed to remove user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to remove user: {e}")
