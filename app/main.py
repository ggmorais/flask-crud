import os
import dotenv

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import sqlalchemy as sql

from datetime import *
from typing import *


dotenv.load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database/db.sqlite3"

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(18), unique=True)
    password = db.Column(db.String(18))
    created_at = db.Column(db.DateTime, default=datetime.now)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    caption = db.Column(db.String(300))
    upvotes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)


def get_columns(tables: db.Model):
    if type(tables) != list:
        tables = [tables]

    return [{col.name: getattr(table, col.name)
             for col in table.__table__.columns} for table in tables]


@app.route("/user", methods=["POST"])
def create_user():
    body = request.json

    email = body.get("email")
    username = body.get("username")
    password = body.get("password")

    error_message = None

    email_exists = User.query.filter_by(email=email).first()
    if email_exists:
        error_message = f"Email '{email}' already in use."

    username_exists = User.query.filter_by(username=username).first()
    if username_exists:
        error_message = f"Username '{username}' already in use."

    if error_message:
        return jsonify({"done": False, "message": error_message})

    user = User(
        email=email,
        username=username,
        password=password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"done": True, "message": "User created successfully.", "user_id": user.id})


@app.route("/user/<user_id>")
def get_user(user_id: int):
    user = User.query.filter_by(id=user_id).first()

    if user:
        return jsonify({"done": True, "user": get_columns(user)})

    return jsonify({"done": False, "message": f"User ID '{user_id}' not found."})


@app.route("/user/<user_id>", methods=["PATCH"])
def modify_user(user_id: int):
    body = request.json

    user = User.query.filter_by(id=user_id).first()

    if "email" in body:
        user.email = body["email"]
    if "username" in body:
        user.username = body["username"]
    if "password" in body:
        user.password = body["password"]

    db.session.commit()

    return jsonify({"done": True, "message": "User informations updated successfully."})


@app.route("/user/<user_id>", methods=["DELETE"])
def delete_user(user_id: int):
    user = User.query.filter_by(id=user_id).first()

    db.session.delete(user)
    db.session.commit()

    return jsonify({"done": True, "message": "User deleted successfully."})


@app.route("/<user_id>/post", methods=["POST"])
def create_post(user_id: int):
    body = request.json

    post = Post(
        user_id=user_id,
        caption=body.get("caption")
    )

    db.session.add(post)
    db.session.commit()

    return jsonify({"done": True, "message": "Post created successfully."})


@app.route("/posts/<user_id>")
@app.route("/posts/<user_id>/<post_id>")
def get_posts(user_id: int, post_id: int = None):
    if post_id:
        posts = Post.query.filter_by(user_id=user_id, id=post_id).first()
    else:
        posts = Post.query.filter_by(user_id=user_id).all()

    return jsonify({"done": True, "posts": get_columns(posts)})


@app.route("/post/<post_id>", methods=["PATCH"])
def modify_post(post_id: int):
    body = request.json

    post = Post.query.filter_by(id=post_id).first()

    if not post:
        return jsonify({"done": False, "message": f"Post ID {post_id} not found."})

    post.caption = body.get("caption")
    post.updated_at = datetime.now()

    db.session.commit()

    return jsonify({"done": True, "message": "Post updated successfully."})


@app.route("/post/<post_id>", methods=["DELETE"])
def delete_post(post_id: int):
    post = Post.query.filter_by(id=post_id).first()

    if not post:
        return jsonify({"done": False, "message": f"Post ID {post_id} not found."})

    db.session.delete(post)
    db.session.commit()

    return jsonify({"done": True, "message": "Post deleted successfully."})


if __name__ == "__main__":
    app.run(debug=os.getenv("DEBUG"), port=os.getenv("PORT"))
