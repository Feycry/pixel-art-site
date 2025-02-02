CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    size TEXT CHECK(size IN ('16x16', '32x32', '64x64')) DEFAULT '32x32',
    palette TEXT, -- Can store palette name or ID for predefined palettes
    likes INTEGER DEFAULT 0,
    state INTEGER DEFAULT 1 -- 1 = active, 0 = deleted
);

CREATE TABLE post_data (
    post_id INTEGER PRIMARY KEY REFERENCES posts(id),
    data BLOB NOT NULL
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE post_tags (
    post_id INTEGER REFERENCES posts(id),
    tag_id INTEGER REFERENCES tags(id),
    PRIMARY KEY (post_id, tag_id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,
    sent_at TEXT DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id),
    post_id INTEGER REFERENCES posts(id),
    state INTEGER DEFAULT 1 -- 1 = active, 0 = deleted
);

CREATE TABLE likes (
    user_id INTEGER REFERENCES users(id),
    post_id INTEGER REFERENCES posts(id),
    PRIMARY KEY (user_id, post_id)
);
