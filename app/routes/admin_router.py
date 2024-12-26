from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

from ..utils.logger_handler import logger
from ..db.config import get_db
from ..models.app_models import Post, User
from ..routes.auth_router import check_admin

admin_route = APIRouter(prefix="/api/v1/admin", tags=["Admin Route"], dependencies=[Depends(check_admin)])


@admin_route.delete(path="/remove/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_inappropriate_posts(post_id: UUID, db: Session = Depends(get_db)):
    is_post = db.query(Post).filter(Post.id == post_id).first()  # type:ignore
    if is_post is None:
        logger.warning(f"Post {post_id} does not Exist!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {post_id} does not found")

    try:
        db.delete(is_post)
        db.commit()
        logger.info(f"Post {is_post.title} removed successfully!")

    except Exception as e:
        logger.error(f"Failed to remove post: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to remove post: {e}")


@admin_route.get("/all/users", status_code=status.HTTP_200_OK)
async def get_all_users(db: Session = Depends(get_db)):
    all_users = db.query(User).all()
    logger.info("All users fetched successfully!")
    return all_users


@admin_route.delete("/remove/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_inactive_user(user_id: UUID, db: Session = Depends(get_db)):
    is_user = db.query(User).filter(User.id == user_id).first()  # type:ignore
    if is_user is None:
        logger.warning(f"User {user_id} does not Exist!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} does not found")
    if is_user.is_admin:
        logger.warning(f"User {user_id} is Admin!")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User {user_id} is Admin!")

    if is_user.is_active:
        logger.warning(f"User {user_id} is active!")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User {user_id} is active!")

    try:
        db.delete(is_user)
        db.commit()
        logger.info(f"User {is_user.username} removed successfully!")

    except Exception as e:
        logger.error(f"Failed to remove user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to remove user: {e}")
