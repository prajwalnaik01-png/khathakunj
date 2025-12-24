from flask import Flask, render_template, request, redirect, session, abort
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "khathakunj_secret"

# ---------------- CONFIG ----------------
ADMIN_USER = "admin"
SUPPORTED_LANGS = ["en", "kn", "hi", "bn"]

def get_db():
    return sqlite3.connect("khathakunj.db")

# ---------------- LANGUAGE ----------------
@app.route("/set-language/<lang>")
def set_language(lang):
    if lang in SUPPORTED_LANGS:
        session["lang"] = lang
    return redirect(request.referrer or "/home")

def get_lang():
    return session.get("lang", "en")

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT password FROM users WHERE username=?", (u,))
        row = cur.fetchone()
        con.close()

        if row and check_password_hash(row[0], p):
            session["user"] = u
            return redirect("/home")

    return render_template("login.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        con = get_db()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users(username,password) VALUES (?,?)",
            (u, generate_password_hash(p))
        )
        con.commit()
        con.close()
        return redirect("/")

    return render_template("register.html")

# ---------------- HOME ----------------
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")
    return render_template("home.html")

# ---------------- ABOUT ----------------
@app.route("/about")
def about():
    return render_template("about.html")

# ---------------- STORIES (SHOW GENRE + LANGUAGE) ----------------
@app.route("/stories")
def stories():
    lang = get_lang()
    con = get_db()
    cur = con.cursor()

    cur.execute("""
        SELECT DISTINCT story_title, genre, lang
        FROM chapters
        WHERE lang=?
        ORDER BY story_title
    """, (lang,))

    stories = cur.fetchall()
    con.close()

    return render_template("stories.html", stories=stories)

# ---------------- CHAPTER LIST ----------------
@app.route("/story/<title>")
def story(title):
    lang = get_lang()
    con = get_db()
    cur = con.cursor()

    cur.execute("""
        SELECT id, chapter_no, chapter_title
        FROM chapters
        WHERE story_title=? AND lang=?
        ORDER BY chapter_no
    """, (title, lang))

    chapters = cur.fetchall()
    con.close()

    if not chapters:
        return "<h3>No chapters found.</h3><a href='/stories'>⬅ Back</a>"

    return render_template("chapters.html", title=title, chapters=chapters)

# ---------------- READ CHAPTER ----------------
@app.route("/chapter/<int:id>")
def chapter(id):
    con = get_db()
    cur = con.cursor()

    cur.execute("""
        SELECT story_title, chapter_no, chapter_title, content
        FROM chapters
        WHERE id=?
    """, (id,))

    chapter = cur.fetchone()
    con.close()

    if not chapter:
        abort(404)

    return render_template("chapter_read.html", chapter=chapter)

# ---------------- DELETE STORY (ADMIN ONLY) ----------------
@app.route("/admin/delete/<title>")
def delete_story(title):
    if session.get("user") != ADMIN_USER:
        abort(403)

    con = get_db()
    cur = con.cursor()
    cur.execute("DELETE FROM chapters WHERE story_title=?", (title,))
    con.commit()
    con.close()

    return redirect("/stories")

# ---------------- EDIT STORY (ADMIN ONLY) ----------------
@app.route("/admin/edit/<title>", methods=["GET", "POST"])
def edit_story(title):
    if session.get("user") != ADMIN_USER:
        abort(403)

    con = get_db()
    cur = con.cursor()

    if request.method == "POST":
        chapter_id = request.form["chapter_id"]
        chapter_title = request.form["chapter_title"]
        content = request.form["content"]

        cur.execute("""
            UPDATE chapters
            SET chapter_title=?, content=?
            WHERE id=?
        """, (chapter_title, content, chapter_id))

        con.commit()
        con.close()
        return redirect("/stories")

    cur.execute("""
        SELECT id, chapter_no, chapter_title, content
        FROM chapters
        WHERE story_title=?
        ORDER BY chapter_no
    """, (title,))
    chapters = cur.fetchall()
    con.close()

    return render_template("edit_story.html", title=title, chapters=chapters)

# ---------------- ADMIN PANEL (NEW STORY + CHAPTER + GENRE + LANG) ----------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if session.get("user") != ADMIN_USER:
        return redirect("/home")

    con = get_db()
    cur = con.cursor()

    if request.method == "POST":
        mode = request.form["mode"]
        story_title = request.form["story_title"]
        chapter_title = request.form["chapter_title"]
        content = request.form["content"]
        genre = request.form["genre"]
        lang = request.form["lang"]

        chapter_no = 1 if mode == "new" else request.form["chapter_no"]

        cur.execute("""
            INSERT INTO chapters
            (story_title, chapter_no, chapter_title, content, genre, lang)
            VALUES (?,?,?,?,?,?)
        """, (story_title, chapter_no, chapter_title, content, genre, lang))

        con.commit()

    cur.execute("SELECT DISTINCT story_title FROM chapters")
    stories = cur.fetchall()
    con.close()

    return render_template("admin.html", stories=stories)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
