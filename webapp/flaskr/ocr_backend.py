from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from flaskr.auth import login_required
from flaskr.db import get_db
import os
from flaskr.handwriting_reader.gcp import GoogleCloudVisionHR

handwriting_reader = GoogleCloudVisionHR()


bp = Blueprint("ocr", __name__)
UPLOAD_FOLDER = "flaskr/static/uploads/images"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# @bp.route('/', methods=['GET', 'POST'])
@bp.route("/", methods=["GET", "POST"])
def index():
    search = request.form.get("search", "")
    db = get_db()
    if not search:
        posts = db.execute(
            "SELECT p.id, title, img_path, ocr_output, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " ORDER BY created DESC"
        ).fetchall()

    else:
        query = """
            SELECT p.id, title, img_path, ocr_output, created, author_id, username
            FROM post p 
            JOIN user u ON p.author_id = u.id
            WHERE title LIKE :search OR ocr_output LIKE :search
            OR img_path LIKE :file_search
            ORDER BY created DESC
        """
        # Handle file search for various extensions
        if search.startswith("*."):
            # Extract file extension (e.g., "jpg", "png")
            file_extension = search[2:]
            file_search = f"%.{file_extension}"
        else:
            file_search = f"%{search}%"
        posts = db.execute(
            query, {"search": f"%{search}%", "file_search": file_search}
        ).fetchall()

    return render_template("ocr/index.html", posts=posts)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        file = request.files["image"]
        error = None

        if not title:
            error = "Title is required."
        elif file.filename == "":
            error = "No selected file."
        elif not allowed_file(file.filename):
            error = "Invalid file type."

        if error is not None:
            flash(error)

        else:
            filename = secure_filename(file.filename)
            img_path = filename
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            root_img_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(
                root_img_path
            )  # Save the file in the flaskr/static/uploads/images directory
            ocr_output = handwriting_reader.read_text(root_img_path)

            db = get_db()
            db.execute(
                "INSERT INTO post (title, img_path, ocr_output, author_id)"
                " VALUES (?, ?, ?, ?)",
                (title, img_path, ocr_output, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("ocr.index"))

    return render_template("ocr/create.html")


def get_post(id, check_author=True):
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, img_path, ocr_output, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        ocr_output = request.form["ocr_output"]
        error = None

        if not title:
            error = "Title is required."
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, ocr_output = ? WHERE id = ?",
                (title, ocr_output, id),
            )
            db.commit()
            return redirect(url_for("ocr.index"))

    return render_template("ocr/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("ocr.index"))
