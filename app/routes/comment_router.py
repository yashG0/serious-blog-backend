from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

from .auth_router import get_current_user
from ..schemas.user_schema import UserOutSchema
from ..utils.logger_handler import logger
from ..db.config import get_db
from ..models.app_models import Post, Comment
from ..schemas.comment_schema import CommentOutSchema, CommentCreateSchema

comment_route = APIRouter(prefix="/api/v1/comment", tags=["My Comment Route"])


@comment_route.get("/all/{post_id}", status_code=status.HTTP_200_OK, response_model=list[CommentOutSchema])
async def get_all_comments(post_id: UUID, db: Session = Depends(get_db)):
    is_post = db.query(Post).filter(Post.id == post_id).first()  # type:ignore
    if is_post is None:
        logger.warning("Post does not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {post_id} does not found")

    all_comments = db.query(Comment).filter(Comment.post_id == post_id).all()  # type:ignore
    return all_comments


@comment_route.post("/create/{post_id}", status_code=status.HTTP_201_CREATED)
async def create_comment(post_id: UUID, new_comment: CommentCreateSchema, db: Session = Depends(get_db),
                         current_user: UserOutSchema = Depends(get_current_user)):
    is_post = db.query(Post).filter(Post.id == post_id).first()  # type:ignore
    if is_post is None:
        logger.warning("Post does not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {post_id} does not found")

    try:
        create_new_comment = Comment(
            content=new_comment.content,
            user_id=current_user.id,
            post_id=post_id
        )
        db.add(create_new_comment)
        db.commit()
        logger.info(f"Comment '{new_comment.content}' created successfully!")

    except Exception as e:
        logger.error(f"Failed to create comment: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create comment: {e}")


@comment_route.delete("/remove/{post_id}/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_comment(post_id: UUID, comment_id: UUID, db: Session = Depends(get_db),
                         current_user: UserOutSchema = Depends(get_current_user)):
    is_post = db.query(Post).filter(Post.id == post_id).first()  # type:ignore
    if is_post is None:
        logger.warning(f"Post {post_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {post_id} does not exist")

    is_comment = db.query(Comment).filter(Comment.user_id == current_user.id).filter(  # type:ignore
        Comment.id == comment_id).first()

    if is_comment is None:
        logger.warning(f"Comment {comment_id} not found for user {current_user.id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comment {comment_id} does not exist")

    try:
        db.delete(is_comment)
        db.commit()
        logger.info(f"Comment '{comment_id}' removed successfully by user {current_user.id}")

    except Exception as e:
        logger.error(f"Failed to remove comment: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to remove comment: {e}")
