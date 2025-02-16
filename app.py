import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, Response, abort
import config, forum, users
import io

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    posts = forum.get_posts()
    print(posts)
    return render_template("index.html", posts=posts)

@app.route("/submit")
def submit():
    return render_template("submit.html")

@app.route("/post/<int:post_id>")
def show_post(post_id):
    post = forum.get_post(post_id)
    comments = forum.get_comments(post_id)
    return render_template("post.html", post=post, comments=comments)

@app.route("/post/<int:post_id>/image")
def get_post_image(post_id):
    post = forum.get_post(post_id)
    if post and post["image_data"]:
        return Response(io.BytesIO(post["image_data"]).getvalue(), mimetype="image/png")
    return "Image not found", 404

@app.route("/new_post", methods=["POST"])
def new_post():
    title = request.form["title"]
    user_id = session.get("user_id")
    
    if not user_id:
        return redirect("/login")

    # Handle image upload
    image = request.files.get("image")
    if not image or image.filename == "":
        return "VIRHE: Kuva puuttuu", 400

    if not image.filename.endswith(".png"):
        return "VIRHE: Vain PNG-kuvat sallittu", 400

    post_id = forum.add_post(title, sqlite3.Binary(image.read()), user_id)
    
    return redirect(f"/post/{post_id}")

@app.route("/new_comment", methods=["POST"])
def new_comment():
    content = request.form["content"]
    user_id = session["user_id"]
    post_id = request.form["post_id"]

    forum.add_comment(content, user_id, post_id)
    return redirect("/post/" + str(post_id))

@app.route("/edit/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(comment_id):
    comment = forum.get_comment(comment_id)

    if not "user_id" in session:
        return redirect("/login")
    if comment["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("edit.html", comment=comment)

    if request.method == "POST":
        content = request.form["content"]
        forum.update_comment(comment["id"], content)
        return redirect("/post/" + str(comment["post_id"]))

@app.route("/remove/<int:comment_id>", methods=["GET", "POST"])
def remove_comment(comment_id):
    comment = forum.get_comment(comment_id)

    if not "user_id" in session:
        return redirect("/login")
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
    return render_template("register.html")

@app.route("/new_user", methods=["GET", "POST"])
def new_user():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]

        if password1 != password2:
            return "VIRHE: salasanat eivät ole samat"

        try:
            users.create_user(username, password1)
            return "Tunnus luotu"
        except sqlite3.IntegrityError:
            return "VIRHE: tunnus on jo varattu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["user_id"]
    return redirect("/")