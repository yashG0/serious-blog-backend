from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..utils.logger_handler import logger
from ..db.config import get_db
from ..models.app_models import User
from ..schemas.user_schema import UserOutSchema, UserCreateSchema
from ..utils.jwt_handler import create_access_token, verify_token
from ..utils.password_handler import hash_password, verify_password

auth_route = APIRouter(prefix="/api/v1/auth", tags=["My auth Router"])

oAuth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@auth_route.post("/signup", response_model=UserOutSchema, status_code=status.HTTP_201_CREATED)
async def create_user(new_user: UserCreateSchema, db: Session = Depends(get_db)):
    is_user_exist = db.query(User).filter(User.email == new_user.email).first()  # type:ignore
    if is_user_exist:
        logger.warning("User already exist!")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exist! please login")

    try:
        hashed_password = hash_password(new_user.password)

        new_user = User(
            username=new_user.username,
            email=new_user.email,
            password=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info("New user created successfully!")
        return new_user

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create new user: {e}")


@auth_route.post("/login", status_code=status.HTTP_200_OK)
async def login_user(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict:
    is_user_exist = db.query(User).filter(User.email == user.username).first()  # type:ignore
    if not is_user_exist:
        logger.warning("User not found!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")

    try:
        is_password_correct = verify_password(user.password, is_user_exist.password)
        if not is_password_correct:
            logger.warning("Invalid password!")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password!")

        token = create_access_token(data={"email": is_user_exist.email})

        logger.info("User logged in successfully!")
        return {
            "access_token": token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to login user: {e}")


def get_current_user(token: str = Depends(oAuth2), db: Session = Depends(get_db)) -> UserOutSchema:
    payload = verify_token(token)

    if not payload:
        logger.warning("Invalid token")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    email = payload.get("email")
    is_user = db.query(User).filter(User.email == email).first()  # type:ignore

    if is_user is None:
        logger.warning("User does not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not found")

    return UserOutSchema(
        id=is_user.id,
        username=is_user.username,
        email=is_user.email,
        is_active=is_user.is_active,
        is_admin=is_user.is_admin,
        created_at=is_user.created_at,
        updated_at=is_user.updated_at
    )


def check_admin(current_user: UserOutSchema = Depends(get_current_user)) -> UserOutSchema:
    if not current_user.is_admin:
        logger.warning(f"User {current_user.username} is not admin")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User {current_user.username} is not admin")
    return current_user
