import db

def get_posts():
    sql = """SELECT t.id, t.title, COUNT(m.id) total, MAX(m.sent_at) last
             FROM posts t, comments m
             WHERE t.id = m.post_id
             GROUP BY t.id
             ORDER BY t.id DESC"""
    return db.query(sql)

def get_post(post_id):
    sql = "SELECT id, title FROM posts WHERE id = ?"
    return db.query(sql, [post_id])[0]

def get_comments(post_id):
    sql = """SELECT m.id, m.content, m.sent_at, m.user_id, u.username
             FROM comments m, users u
             WHERE m.user_id = u.id AND m.post_id = ? AND m.state = 1
             ORDER BY m.id"""
    return db.query(sql, [post_id])

def get_comment(comment_id):
    sql = "SELECT id, content, user_id, post_id FROM comments WHERE id = ?"
    return db.query(sql, [comment_id])[0]

def add_post(title, content, user_id):
    sql = "INSERT INTO posts (title, user_id) VALUES (?, ?)"
    db.execute(sql, [title, user_id])
    post_id = db.last_insert_id()
    add_comment(content, user_id, post_id)
    return post_id

def add_comment(content, user_id, post_id):
    sql = """INSERT INTO comments (content, sent_at, user_id, post_id) VALUES
             (?, datetime('now'), ?, ?)"""
    db.execute(sql, [content, user_id, post_id])

def update_comment(comment_id, content):
    sql = "UPDATE comments SET content = ? WHERE id = ?"
    db.execute(sql, [content, comment_id])

def remove_comment(comment_id):
    sql = "UPDATE comments SET state = 0 WHERE id = ?"
    db.execute(sql, [comment_id])