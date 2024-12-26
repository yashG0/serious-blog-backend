from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import UUID4
from sqlalchemy.orm import Session

from .auth_router import check_admin
from ..schemas.user_schema import UserOutSchema
from ..utils.logger_handler import logger

from ..db.config import get_db
from ..models.app_models import Category
from ..schemas.category_schema import CategoryOutSchema, CategoryCreateSchema

category_route = APIRouter(prefix="/api/v1/category", tags=["Category Router"])


@category_route.get(path="/all", status_code=status.HTTP_200_OK, response_model=list[CategoryOutSchema],
                    name="all_categories")
async def get_all_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@category_route.get(path="by_id/{category_id}", status_code=status.HTTP_200_OK, response_model=CategoryOutSchema,
                    name="category_by_id")
async def get_category_by_id(category_id: UUID4, db: Session = Depends(get_db)):
    is_category = db.query(Category).filter(Category.id == category_id).first()  # type:ignore
    if is_category is None:
        logger.warning("Category does not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category {category_id} does not found")
    return is_category


@category_route.post(path="/create", status_code=status.HTTP_201_CREATED,
                     name="create_category")
async def create_category(new_category: CategoryCreateSchema, db: Session = Depends(get_db),
                          is_admin: UserOutSchema = Depends(check_admin)):
    if is_admin:
        create_new_category = Category(
            name=new_category.name,
            description=new_category.description
        )
        db.add(create_new_category)
        db.commit()
        db.refresh(create_new_category)
        logger.info(f"Category {create_new_category.name} created successfully!")


@category_route.delete(path="/remove/{category_id}", status_code=status.HTTP_204_NO_CONTENT,
                       name="remove_category_by_id")
async def remove_category_by_id(category_id: UUID4, db: Session = Depends(get_db),
                                is_admin: UserOutSchema = Depends(check_admin)):
    try:
        if is_admin:
            is_category = db.query(Category).filter(Category.id == category_id).first()  # type:ignore
            db.delete(is_category)
            db.commit()
            logger.info(f"Category {category_id} removed successfully!")
    except Exception as e:
        logger.error(f"Failed to remove category: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to remove category: {e}")
