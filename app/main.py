from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routes import auth_router, user_router, category_router, post_router, comment_router, admin_router
from .db.config import base, engine
from dotenv import load_dotenv


base.metadata.create_all(bind=engine)

load_dotenv()

app = FastAPI(
    title="BlogMaster APP",
    description="A comprehensive API for creating, managing, and interacting with blog posts and comments.",
    version="1.0.0",
)

# Mounting static file in fastapi app ->
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router.auth_route)
app.include_router(user_router.user_route)
app.include_router(admin_router.admin_route)
app.include_router(category_router.category_route)
app.include_router(post_router.post_route)
app.include_router(comment_router.comment_route)
