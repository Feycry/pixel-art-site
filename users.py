from werkzeug.security import check_password_hash, generate_password_hash
import db
from flask import session, abort

def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def check_login(username, password):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])

    if len(result) == 1:
        user_id, password_hash = result[0]
        if check_password_hash(password_hash, password):
            return user_id

    return None

def require_login():
    if "user_id" not in session:
        return abort(403)

def get_user(user_id):
    sql = "SELECT username FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_comments(user_id):
    sql = """SELECT c.id,
                    c.post_id,
                    p.title thread_title,
                    c.sent_at
             FROM posts p, comments c
             WHERE p.id = c.post_id AND
                   c.user_id = ?
             ORDER BY c.sent_at DESC"""
    return db.query(sql, [user_id])
