import sqlite3

con = sqlite3.connect("khathakunj.db")
cur = con.cursor()

# ---------- USERS TABLE ----------
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# ---------- CHAPTERS TABLE ----------
cur.execute("""
CREATE TABLE IF NOT EXISTS chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_title TEXT NOT NULL,
    chapter_no INTEGER NOT NULL,
    chapter_title TEXT NOT NULL,
    content TEXT NOT NULL,
    genre TEXT,
    lang TEXT
)
""")

con.commit()
con.close()

print("✅ Database initialized successfully")
