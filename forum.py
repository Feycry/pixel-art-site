import db

def get_posts():
    sql = """SELECT t.id, t.title, COUNT(m.id) total, MAX(m.sent_at) last
             FROM posts t
             LEFT JOIN comments m ON t.id = m.post_id
             WHERE t.state = 1
             GROUP BY t.id
             ORDER BY t.id DESC"""
    return db.query(sql)

def get_post(post_id):
    sql = "SELECT id, title, image_data FROM posts WHERE id = ?"
    return db.query(sql, [post_id])[0]

def get_comments(post_id):
    sql = """SELECT c.id, c.content, c.sent_at, c.user_id, u.username
             FROM comments c, users u
             WHERE c.user_id = u.id AND c.post_id = ? AND c.state = 1
             ORDER BY c.id"""
    return db.query(sql, [post_id])

def get_comment(comment_id):
    sql = "SELECT id, content, user_id, post_id FROM comments WHERE id = ?"
    return db.query(sql, [comment_id])[0]

def add_post(title, image, user_id):
    sql = "INSERT INTO posts (title, image_data, user_id) VALUES (?, ?, ?)"
    db.execute(sql, [title, image, user_id])
    return db.last_insert_id()

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