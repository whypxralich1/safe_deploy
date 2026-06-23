"""
FastAPI приложение для Корпоративного файлового менеджера
Включает:
- Регистрацию пользователей с валидацией (Задание 4)
- Комментарии с защитой от XSS (Задание 6)
- RBAC с защитой от IDOR (Задание 8)
"""

from fastapi import FastAPI, HTTPException, Form, Depends, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime
from typing import Optional
from src.schemas import UserCreate
from src.sanitizer import sanitize_comment

# ========================================
# 1. СОЗДАНИЕ ПРИЛОЖЕНИЯ
# ========================================

app = FastAPI(
    title="Корпоративный файловый менеджер",
    description="API для управления файлами с защитой от XSS и IDOR",
    version="2.0.0"
)

# ========================================
# 2. ДАННЫЕ ДЛЯ ЗАДАНИЯ 4 (Регистрация)
# ========================================

# Хранилище комментариев (в памяти)
comments_store = []

# ========================================
# 3. ДАННЫЕ ДЛЯ ЗАДАНИЯ 8 (RBAC)
# ========================================

# База пользователей
users_db = {
    "alice": {"password": "alice123", "role": "user"},
    "bob": {"password": "bob123", "role": "user"},
    "admin": {"password": "admin123", "role": "admin"}
}

# База файлов
files_db = [
    {"id": 1, "name": "alice_report.pdf", "owner": "alice", "size": 1024, "content": "Alice's secret report"},
    {"id": 2, "name": "bob_report.pdf", "owner": "bob", "size": 2048, "content": "Bob's financial data"},
    {"id": 3, "name": "admin_audit.pdf", "owner": "admin", "size": 4096, "content": "System audit log"}
]

# ========================================
# 4. ФУНКЦИИ АВТОРИЗАЦИИ (Задание 8)
# ========================================

def get_current_user(username: Optional[str] = Header(None, alias="X-Username")):
    """Получение текущего пользователя из заголовка"""
    if not username or username not in users_db:
        raise HTTPException(status_code=401, detail="Invalid user")
    return username


def get_user_role(username: str) -> str:
    """Получить роль пользователя"""
    return users_db.get(username, {}).get("role", "user")


def check_file_permissions(file_id: int, current_user: str = Depends(get_current_user)):
    """Проверка прав доступа к файлу"""
    file = next((f for f in files_db if f["id"] == file_id), None)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    user_role = get_user_role(current_user)
    if user_role == "admin" or file["owner"] == current_user:
        return file
    raise HTTPException(status_code=404, detail="File not found")

# ========================================
# 5. КОРНЕВОЙ ЭНДПОИНТ
# ========================================

@app.get("/")
async def root():
    return {
        "message": "Welcome to Corporate File Manager API",
        "endpoints": {
            "docs": "/docs",
            "registration": "/registration (POST)",
            "comments": "/comments (GET, POST)",
            "files": {
                "get_file": "/files/{file_id} (GET)",
                "delete_file": "/files/{file_id} (DELETE)",
                "my_files": "/files/my (GET)",
                "all_files": "/files/all (GET) - admin only"
            }
        }
    }

# ========================================
# 6. ЭНДПОИНТЫ ЗАДАНИЯ 4 (Регистрация)
# ========================================

@app.post("/registration")
async def register_user(user_data: UserCreate):
    """Регистрация нового пользователя"""
    try:
        if user_data.username in users_db:
            raise HTTPException(status_code=400, detail="Username already exists")
        return {
            "msg": "User created",
            "user": user_data.username,
            "email": user_data.email,
            "age": user_data.age
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

# ========================================
# 7. ЭНДПОИНТЫ ЗАДАНИЯ 6 (Комментарии)
# ========================================

def render_comments_html():
    """Генерирует HTML страницу с комментариями"""
    comments_html = ""
    if comments_store:
        for i, comment in enumerate(comments_store):
            comments_html += f"""
            <div class="comment">
                <div class="meta">#{i+1} • {comment['timestamp']}</div>
                <div class="content">{comment['text']}</div>
            </div>
            """
    else:
        comments_html = '<p class="empty">Пока нет комментариев. Будьте первым!</p>'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>📝 Стена комментариев</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                border-bottom: 2px solid #4CAF50;
                padding-bottom: 10px;
            }}
            .comment-form {{
                margin: 20px 0;
            }}
            .comment-form textarea {{
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                resize: vertical;
                min-height: 100px;
                font-size: 14px;
                box-sizing: border-box;
            }}
            .comment-form button {{
                background: #4CAF50;
                color: white;
                padding: 10px 30px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin-top: 10px;
            }}
            .comment-form button:hover {{
                background: #45a049;
            }}
            .comments-list {{
                margin-top: 30px;
            }}
            .comment {{
                background: #f9f9f9;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #4CAF50;
                border-radius: 5px;
            }}
            .comment .meta {{
                color: #666;
                font-size: 12px;
                margin-bottom: 5px;
            }}
            .comment .content {{
                font-size: 14px;
                word-wrap: break-word;
            }}
            .empty {{
                color: #999;
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📝 Стена комментариев</h1>

            <div class="comment-form">
                <form method="POST" action="/comments">
                    <textarea name="comment" placeholder="Напишите ваш комментарий..." required></textarea>
                    <br>
                    <button type="submit">Отправить комментарий</button>
                </form>
            </div>

            <div class="comments-list">
                <h2>Все комментарии ({len(comments_store)})</h2>
                {comments_html}
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/comments", response_class=HTMLResponse)
async def get_comments():
    return HTMLResponse(content=render_comments_html())


@app.post("/comments", response_class=HTMLResponse)
async def post_comments(comment: str = Form(...)):
    cleaned_text = sanitize_comment(comment)
    comments_store.append({
        "text": cleaned_text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return RedirectResponse(url="/comments", status_code=303)

# ========================================
# 8. ЭНДПОИНТЫ ЗАДАНИЯ 8 (RBAC)
# ========================================

# ✅ СПЕЦИФИЧНЫЕ МАРШРУТЫ - ДОЛЖНЫ БЫТЬ ПЕРВЫМИ!

@app.get("/files/my")
async def get_my_files(current_user: str = Depends(get_current_user)):
    """Получение списка файлов текущего пользователя"""
    user_files = [f for f in files_db if f["owner"] == current_user]
    return {
        "user": current_user,
        "files": user_files,
        "count": len(user_files)
    }


@app.get("/files/all")
async def get_all_files(current_user: str = Depends(get_current_user)):
    """Получение списка всех файлов (только для админа)"""
    user_role = get_user_role(current_user)
    if user_role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return {
        "total": len(files_db),
        "files": files_db
    }


# ✅ ДИНАМИЧЕСКИЙ МАРШРУТ - ДОЛЖЕН БЫТЬ ПОСЛЕДНИМ!

@app.get("/files/{file_id}")
async def get_file(file: dict = Depends(check_file_permissions)):
    """Получение информации о файле по ID"""
    return {
        "id": file["id"],
        "name": file["name"],
        "owner": file["owner"],
        "size": file["size"],
        "content": file["content"]
    }


@app.delete("/files/{file_id}")
async def delete_file(
    file_id: int,
    current_user: str = Depends(get_current_user),
    file: dict = Depends(check_file_permissions)
):
    """Удаление файла по ID"""
    global files_db
    files_db = [f for f in files_db if f["id"] != file_id]
    return {
        "msg": f"File {file_id} deleted successfully",
        "deleted_by": current_user,
        "remaining_files": len(files_db)
    }


@app.get("/files")
async def list_all_files():
    """Вспомогательный эндпоинт для просмотра всех файлов (без авторизации)"""
    return {
        "total": len(files_db),
        "files": files_db
    }
