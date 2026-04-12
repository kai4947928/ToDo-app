from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

#ログイン画面表示とホーム画面表示
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email").strip()
        password = request.form.get("password")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if user is None:
            flash("メールアドレスまたはパスワードが正しくありません")
            return render_template("auth/login.html")

        if not check_password_hash(user["password_hash"], password):
            flash("メールアドレスまたはパスワードが正しくありません")
            return render_template("auth/login.html")

        session.clear()
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]

        flash("ログインしました。")
        return redirect(url_for("home"))
    return render_template("auth/login.html")

#新規登録と登録時のエラーメッセージの表示
@auth_bp.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()
        password_confirm = request.form.get("password_confirm")

        errors = []

        if not name:
            errors.append("名前は必須です。")

        if not email:
            errors.append("メールアドレスは必須です。")

        if not password:
            errors.append("パスワードは必須です。")

        if len(password) < 8:
            errors.append("パスワードは8文字以上で入力してください")

        if password != password_confirm:
            errors.append("パスワードが一致しません。")

        db = get_db()
        existing_user = db.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing_user:
            errors.append("このメールアドレスはすでに登録さています。")

        if errors:
            for error in errors:
                flash(error)
            return render_template("auth/register.html")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        password_hash = generate_password_hash(password)

        db.execute(
            """
            INSERT INTO users (name, email, password_hash, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, password_hash, now, now)
        )
        db.commit()

        flash("登録が完了しました。ログインしてください。")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("ログアウトしました。")
    return redirect(url_for("auth.login"))