from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime
import re

app = FastAPI()
comments_store = []


def sanitize_comment(text: str) -> str:
    # Удаляем все теги <script>
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL)
    # Удаляем обработчики событий onerror, onclick и т.д.
    text = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', text)
    # Удаляем теги <img>
    text = re.sub(r'<img.*?>', '', text, flags=re.DOTALL)
    # Удаляем теги <iframe>
    text = re.sub(r'<iframe.*?>.*?</iframe>', '', text, flags=re.DOTALL)
    return text


def render_comments():
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
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #f5f5f5; }}
            .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
            .comment-form {{ margin: 20px 0; }}
            .comment-form textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; resize: vertical; min-height: 100px; font-size: 14px; box-sizing: border-box; }}
            .comment-form button {{ background: #4CAF50; color: white; padding: 10px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-top: 10px; }}
            .comment-form button:hover {{ background: #45a049; }}
            .comments-list {{ margin-top: 30px; }}
            .comment {{ background: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; border-radius: 5px; }}
            .comment .meta {{ color: #666; font-size: 12px; margin-bottom: 5px; }}
            .comment .content {{ font-size: 14px; word-wrap: break-word; }}
            .empty {{ color: #999; font-style: italic; }}
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
    return HTMLResponse(content=render_comments())


@app.post("/comments", response_class=HTMLResponse)
async def post_comments(comment: str = Form(...)):
    cleaned_text = sanitize_comment(comment)
    comments_store.append({
        "text": cleaned_text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return RedirectResponse(url="/comments", status_code=303)
