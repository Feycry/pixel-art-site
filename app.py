import sqlite3
from flask import Flask, redirect, render_template, request, session, Response, abort, flash
import config, forum, users
from users import require_login
import io
import re
import secrets
import markupsafe

app = Flask(__name__)
app.secret_key = config.secret_key

def check_csrf():
    if request.method == "POST":
        token = request.form.get("csrf_token")
    else:
        token = request.args.get("csrf_token")
    if not token or token != session.get("csrf_token"):
        abort(403)

@app.before_request
def before_request():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.route("/")
def index():
    posts = forum.get_posts()
    return render_template("index.html", posts=posts)

@app.route("/submit")
def submit():
    return render_template("submit.html")

@app.route("/post/<int:post_id>")
def show_post(post_id):
    post = forum.get_post(post_id)

    if not post:
        abort(404)

    comments = forum.get_comments(post_id)
    tags = forum.get_tags(post_id)
    user = users.get_user(post["user_id"])[0]
    return render_template("post.html", post=post, comments=comments, tags=tags, user=user)

@app.route("/post/<int:post_id>/image")
def get_post_image(post_id):
    post = forum.get_post(post_id)
    if post and post["image_data"]:
        return Response(io.BytesIO(post["image_data"]).getvalue(), mimetype="image/png")
    return "Image not found", 404

@app.route("/new_post", methods=["POST"])
def new_post():
    require_login()
    check_csrf()

    title = request.form["title"].strip()
    user_id = session.get("user_id")
    tags = request.form["tags"]

    if not title or len(title) > 100:
        flash("VIRHE: Otsikko on pakollinen ja sen pituus saa olla enintään 100 merkkiä")
        return redirect("/submit")

    image = request.files.get("image")
    if not image or image.filename == "":
        flash("VIRHE: Kuva puuttuu")
        return redirect("/submit")

    if not image.filename.endswith(".png"):
        flash("VIRHE: Vain PNG-kuvat sallittu")
        return redirect("/submit")

    try:
        post_id = forum.add_post(title, sqlite3.Binary(image.read()), user_id)
        if tags:
            unique_tags = set()
            for tag in tags.split(","):
                tag = tag.strip()
                if len(tag) > 32:
                    flash("VIRHE: Tagin pituus saa olla enintään 32 merkkiä")
                    return redirect("/submit")
                if tag in unique_tags:
                    continue
                unique_tags.add(tag)
                forum.add_tag_to_post(post_id, tag)
    except sqlite3.IntegrityError:
        abort(403)
    
    return redirect(f"/post/{post_id}")

@app.route("/new_comment", methods=["POST"])
def new_comment():
    require_login()
    check_csrf()

    content = request.form["content"].strip()
    user_id = session["user_id"]
    post_id = request.form["post_id"]

    if not content or len(content) > 5000:
        flash("VIRHE: Kommentti ei saa olla tyhjä ja sen pituus saa olla enintään 5000 merkkiä")
        return redirect(f"/post/{post_id}")

    if not post_id or not post_id.isdigit():
        flash("VIRHE: Virheellinen post ID")
        return redirect(f"/post/{post_id}")

    forum.add_comment(content, user_id, post_id)
    return redirect("/post/" + str(post_id))

@app.route("/edit/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(comment_id):
    require_login()
    
    comment = forum.get_comment(comment_id)

    if not comment:
        flash("VIRHE: Kommentti ei voi olla tyhjä")
        return redirect(f"/edit/{comment_id}")

    if comment["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("edit.html", comment=comment)

    if request.method == "POST":
        check_csrf()
        content = request.form["content"]

        if not content or len(content) > 5000:
            flash("VIRHE: Kommentti ei saa olla tyhjä ja sen pituus saa olla enintään 5000 merkkiä")
            return redirect(f"/edit/{comment_id}")

        forum.update_comment(comment["id"], content)
        return redirect("/post/" + str(comment["post_id"]))

@app.route("/remove/<int:comment_id>", methods=["GET", "POST"])
def remove_comment(comment_id):
    require_login()
    check_csrf()

    comment = forum.get_comment(comment_id)

    if not comment:
        abort(404)

    if comment["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove.html", comment=comment)

    if request.method == "POST":
        if "continue" in request.form:
            forum.remove_comment(comment["id"])
        return redirect("/post/" + str(comment["post_id"]))

@app.route("/register")
def register():
    return render_template("register.html", filled={})

@app.route("/new_user", methods=["GET", "POST"])
def new_user():
    check_csrf()
    if request.method == "GET":
        return render_template("register.html", filled={})

    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]

        if not username or not password1 or not password2:
            flash("VIRHE: Tunnus ja salasana ovat pakollisia")
            filled = {"username": username}
            return render_template("register.html", filled=filled)

        if password1 != password2:
            flash("VIRHE: salasanat eivät ole samat")
            filled = {"username": username}
            return render_template("register.html", filled=filled)

        if len(username) < 3 or len(username) > 20:
            flash("VIRHE: Tunnuksen pituus tulee olla 3-20 merkkiä")
            filled = {"username": username}
            return render_template("register.html", filled=filled)

        if len(password1) < 6:
            flash("VIRHE: Salasanan pituus tulee olla vähintään 6 merkkiä")
            filled = {"username": username}
            return render_template("register.html", filled=filled)

        if not re.match("^[a-zA-Z0-9_]+$", username):
            flash("VIRHE: Tunnus saa sisältää vain kirjaimia, numeroita ja alaviivoja")
            filled = {"username": username}
            return render_template("register.html", filled=filled)

        try:
            users.create_user(username, password1)
            flash("Tunnus luotu")
            return redirect("/login")
        except sqlite3.IntegrityError:
            flash("VIRHE: tunnus on jo varattu")
            filled = {"username": username}
            return render_template("register.html", filled=filled)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        next_page = request.args.get("next_page", request.referrer)
        return render_template("login.html", next_page=next_page)

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        next_page = request.form["next_page"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["csrf_token"] = secrets.token_hex(16)
            return redirect(next_page or "/")
        else:
            flash("VIRHE: Väärä tunnus tai salasana")
            return render_template("login.html", next_page=next_page)

@app.route("/logout")
def logout():
    del session["user_id"]
    return redirect("/")

@app.route("/search")
def search():
    query = request.args.get("query")
    if not query:
        return redirect("/")
    
    posts = forum.search(query)
    return render_template("index.html", posts=posts)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    comments = users.get_comments(user_id)
    posts = forum.get_user_posts(user_id)
    return render_template("user.html", user=user, comments=comments, posts=posts)
