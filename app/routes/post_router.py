from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from uuid import UUID

from .auth_router import check_admin, get_current_user
from ..db.config import get_db
from ..models.app_models import Post, Category
from ..schemas.post_schema import PostOutSchema
from ..schemas.user_schema import UserOutSchema
from ..utils.logger_handler import logger
from ..utils.upload_image_handler import upload_image_handler

post_route = APIRouter(prefix="/api/v1/posts", tags=["My Post Route"])


@post_route.get("/all", response_model=list[PostOutSchema], status_code=status.HTTP_200_OK, )
async def get_posts(db: Session = Depends(get_db)):
    logger.info("All posts fetched successfully!")
    return db.query(Post).all()


@post_route.get("/{post_id}", response_model=PostOutSchema, status_code=status.HTTP_200_OK)
async def get_post_by_id(post_id: UUID, db: Session = Depends(get_db)):
    is_post = db.query(Post).filter(Post.id == post_id).first()  # type:ignore
    if is_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {post_id} does not found")
    logger.info(f"Post {is_post.title} fetched successfully!")
    return is_post


@post_route.post("/create", status_code=status.HTTP_201_CREATED)
async def create_post(new_title: str = Form(..., min_length=3, max_length=100),
                      new_content: str = Form(..., min_length=3),
                      new_category_id: UUID = Form(...),
                      image: UploadFile = File(...), db: Session = Depends(get_db),
                      current_user: UserOutSchema = Depends(get_current_user)):
    is_category_available = db.query(Category).filter(Category.id == new_category_id).first()  # type:ignore
    if is_category_available is None:
        logger.warning("Category does not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Category {new_category_id} does not found")

    unique_filename = await upload_image_handler(image)

    create_new_post = Post(
        title=new_title,
        content=new_content,
        image=unique_filename,
        category_id=new_category_id,
        user_id=current_user.id
    )
    try:
        db.add(create_new_post)
        db.commit()
        logger.info(f"Post '{new_title}' created successfully!")
    except Exception as e:
        logger.error(f"Failed to create post: {new_title}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create post: {e}")


@post_route.get("/all/by_user", status_code=status.HTTP_200_OK)
async def get_post_by_id(db: Session = Depends(get_db), current_user: UserOutSchema = Depends(get_current_user)):
    fetch_posts_of_user = db.query(Post).filter(Post.user_id == current_user.id).all()  # type:ignore
    return fetch_posts_of_user


@post_route.get("/all/by_category/{category_id}", response_model=list[PostOutSchema], status_code=status.HTTP_200_OK)
async def get_post_by_id(category_id: UUID, db: Session = Depends(get_db)):
    is_category = db.query(Category).filter(Category.id == category_id).first()  # type:ignore

    if is_category is None:
        logger.warning("Category does not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category {category_id} does not found")

    all_posts_by_category = db.query(Post).filter(Post.category_id == category_id).all()  # type:ignore
    return all_posts_by_category


@post_route.get("/by_user/{post_id}", response_model=PostOutSchema, status_code=status.HTTP_200_OK)
async def get_post_by_id(post_id: UUID, db: Session = Depends(get_db),
                         current_user: UserOutSchema = Depends(get_current_user)):
    is_post = db.query(Post).filter(Post.user_id == current_user.id).filter(Post.id == post_id).first()  # type:ignore
    if is_post is None:
        logger.warning("Post does not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {post_id} does not found")
    logger.info(f"Post {is_post.title} fetched successfully!")
    return is_post


@post_route.put("/update/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_post_by_id(new_post_data: PostOutSchema, post_id: UUID, db: Session = Depends(get_db),
                            current_user: UserOutSchema = Depends(get_current_user)):
    is_post = db.query(Post).filter(Post.user_id == current_user.id).filter(  # type:ignore
        Post.id == new_post_data.id).first()
    if is_post is None:
        logger.warning("Post does not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {post_id} does not found")

    try:
        is_post.title = new_post_data.title if new_post_data.title else is_post.title
        is_post.content = new_post_data.content if new_post_data.content else is_post.content
        is_post.category_id = new_post_data.category_id if new_post_data.category_id else is_post.category_id
        is_post.image = new_post_data.image if new_post_data.image else is_post.image

        db.commit()
        logger.info(f"Post {is_post.title} updated successfully!")
    except Exception as e:
        logger.error(f"Failed to update post: {is_post.title}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update post: {e}")


@post_route.delete("/remove/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_post_by_id(post_id: UUID,
                            db: Session = Depends(get_db),
                            current_user: UserOutSchema = Depends(get_current_user)):
    is_post = db.query(Post).filter(Post.user_id == current_user.id).filter(Post.id == post_id).first()  # type:ignore

    if is_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {post_id} does not found")
    try:
        db.delete(is_post)
        db.commit()
        logger.info(f"Post {post_id} removed successfully!")
    except Exception as e:
        logger.error(f"Failed to remove post: {post_id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to remove post: {e}")
