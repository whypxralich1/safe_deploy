from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from src.schemas import UserCreate

app=FastAPI(
    title="Корпоративный файловый менеджер",
    description="API для регистрации пользователей",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Corporate File Manager API",
        "docs": "/docs",
        "registration": "/registration"
    }

@app.post("/registration")
async def register_user(user_data: UserCreate):
    try:
        return {
            "msg": "User created",
            "user": user_data.username,
            "email": user_data.email,
            "age": user_data.age
        }
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
