"""
FastAPI приложение для Корпоративного файлового менеджера
Включает:
- Регистрацию пользователей с валидацией (Задание 4)
- Комментарии с защитой от XSS (Задание 6)
- RBAC с защитой от IDOR (Задание 8)
- Безопасную загрузку и скачивание файлов (Задание 9)
"""

from fastapi import FastAPI, HTTPException, Form, Depends, Header, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from datetime import datetime
from typing import Optional
import os
import uuid
import filetype
from pathlib import Path
from src.schemas import UserCreate
from src.sanitizer import sanitize_comment

# ========================================
# 1. СОЗДАНИЕ ПРИЛОЖЕНИЯ
# ========================================

app = FastAPI(
    title="Корпоративный файловый менеджер",
    description="API для управления файлами с защитой от XSS, IDOR и безопасной загрузкой",
    version="3.0.0"
)

# ========================================
# 2. НАСТРОЙКИ ДЛЯ ЗАДАНИЯ 9 (Файлы)
# ========================================

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 МБ
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png"]
STORAGE_DIR = Path("storage")
STORAGE_DIR.mkdir(exist_ok=True)  # Создаем папку, если ее нет

# ========================================
# 3. ДАННЫЕ ДЛЯ ЗАДАНИЯ 4 (Комментарии)
# ========================================

comments_store = []

# ========================================
# 4. ДАННЫЕ ДЛЯ ЗАДАНИЯ 8 (RBAC)
# ========================================

# База пользователей
users_db = {
    "alice": {"password": "alice123", "role": "user"},
    "bob": {"password": "bob123", "role": "user"},
    "admin": {"password": "admin123", "role": "admin"}
}

# База файлов (метаданные)
files_db = [
    {"id": 1, "name": "alice_report.pdf", "owner": "alice", "size": 1024, "content": "Alice's secret report", "path": None},
    {"id": 2, "name": "bob_report.pdf", "owner": "bob", "size": 2048, "content": "Bob's financial data", "path": None},
    {"id": 3, "name": "admin_audit.pdf", "owner": "admin", "size": 4096, "content": "System audit log", "path": None}
]

# ========================================
# 5. ФУНКЦИИ АВТОРИЗАЦИИ (Задание 8)
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
# 6. КОРНЕВОЙ ЭНДПОИНТ
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
                "upload": "/files/upload (POST)",
                "download": "/files/{file_id}/download (GET)",
                "get_file": "/files/{file_id} (GET)",
                "delete_file": "/files/{file_id} (DELETE)",
                "my_files": "/files/my (GET)",
                "all_files": "/files/all (GET) - admin only"
            }
        }
    }

# ========================================
# 7. ЭНДПОИНТЫ ЗАДАНИЯ 4 (Регистрация)
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
# 8. ЭНДПОИНТЫ ЗАДАНИЯ 6 (Комментарии)
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
    """Страница с комментариями"""
    return HTMLResponse(content=render_comments_html())


@app.post("/comments", response_class=HTMLResponse)
async def post_comments(comment: str = Form(...)):
    """Добавление комментария с защитой от XSS"""
    cleaned_text = sanitize_comment(comment)
    comments_store.append({
        "text": cleaned_text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return RedirectResponse(url="/comments", status_code=303)

# ========================================
# 9. ЭНДПОИНТЫ ЗАДАНИЯ 8 (RBAC)
# ========================================

# СПЕЦИФИЧНЫЕ МАРШРУТЫ (должны быть первыми)
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


# ДИНАМИЧЕСКИЙ МАРШРУТ (должен быть после специфичных)
@app.get("/files/{file_id}")
async def get_file(file: dict = Depends(check_file_permissions)):
    """Получение информации о файле по ID"""
    return {
        "id": file["id"],
        "name": file["name"],
        "owner": file["owner"],
        "size": file["size"],
        "path": file.get("path"),
        "content": file.get("content", "File content not available")
    }


@app.delete("/files/{file_id}")
async def delete_file(
    file_id: int,
    current_user: str = Depends(get_current_user),
    file: dict = Depends(check_file_permissions)
):
    """Удаление файла по ID (также удаляет с диска)"""
    global files_db

    # Удаляем файл с диска, если он существует
    if file.get("path"):
        file_path = Path(file["path"])
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                print(f"Warning: Could not delete file from disk: {e}")

    # Удаляем из базы
    files_db = [f for f in files_db if f["id"] != file_id]

    return {
        "msg": f"File {file_id} deleted successfully",
        "deleted_by": current_user,
        "remaining_files": len(files_db)
    }


# ========================================
# 10. ЭНДПОИНТЫ ЗАДАНИЯ 9 (Загрузка и скачивание)
# ========================================

@app.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """
    Загрузка файла с проверкой размера и типа

    - Максимальный размер: 2 МБ
    - Разрешены только: image/jpeg, image/png
    - Проверка по содержимому (magic bytes)
    """
    try:
        # 1. Читаем содержимое файла
        content = await file.read()

        # 2. Проверка размера
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)} MB"
            )

        # 3. Проверка типа по содержимому (magic bytes)
        file_type = filetype.guess(content)
        if not file_type:
            raise HTTPException(
                status_code=400,
                detail="Cannot determine file type. Only JPEG and PNG are allowed."
            )

        # Проверяем MIME-тип
        if file_type.mime not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{file_type.mime}' not allowed. Only JPEG and PNG are supported."
            )

        # 4. Генерируем уникальное имя
        file_uuid = uuid.uuid4()
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
        new_filename = f"{file_uuid}.{file_extension}"
        file_path = STORAGE_DIR / new_filename

        # 5. Сохраняем файл
        with open(file_path, "wb") as f:
            f.write(content)

        # 6. Сохраняем метаданные в files_db
        new_file = {
            "id": len(files_db) + 1,
            "name": file.filename,
            "owner": current_user,
            "size": len(content),
            "path": str(file_path),
            "uuid": str(file_uuid),
            "mime_type": file_type.mime
        }
        files_db.append(new_file)

        return {
            "msg": "File uploaded successfully",
            "file_id": new_file["id"],
            "filename": file.filename,
            "size": len(content),
            "owner": current_user,
            "stored_as": new_filename
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/files/{file_id}/download")
async def download_file(
    file_id: int,
    current_user: str = Depends(get_current_user)
):
    """
    Скачивание файла с проверкой прав доступа

    - Только владелец или админ могут скачать
    - Файл скачивается с оригинальным именем
    - Content-Disposition: attachment (скачивание, а не открытие)
    """
    # 1. Проверяем права доступа через существующую зависимость
    file = check_file_permissions(file_id, current_user)

    # 2. Проверяем, существует ли файл на диске
    if not file.get("path"):
        raise HTTPException(status_code=404, detail="File not found on disk (no path)")

    file_path = Path(file["path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    # 3. Возвращаем файл с оригинальным именем
    return FileResponse(
        path=file_path,
        filename=file["name"],  # Оригинальное имя
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename=\"{file['name']}\""
        }
    )


# ВСПОМОГАТЕЛЬНЫЙ МАРШРУТ (без авторизации)
@app.get("/files")
async def list_all_files():
    """Вспомогательный эндпоинт для просмотра всех файлов (без авторизации)"""
    return {
        "total": len(files_db),
        "files": files_db
    }
