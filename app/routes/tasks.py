from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from datetime import datetime
from app.db import get_db

tasks_bp = Blueprint("tasks", __name__)

#ログイン状態であればタスク一覧画面へ遷移、ログイン状態でなければログイン画面へ遷移
@tasks_bp.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("tasks.task_list"))
    return redirect(url_for("auth.login"))

#ログイン状態であれば、DBからタスク一覧を画面に表示させる
@tasks_bp.route("/tasks")
def task_list():
    if "user_id" not in session:
        flash("ログインが必要です。", "error")
        return redirect(url_for("auth.login"))

    db = get_db()
    tasks = db.execute(
        """
        SELECT id, title, description, start_date, end_date, start_time, end_time, status, created_at, updated_at
        FROM tasks
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    return render_template("tasks/list.html", tasks=tasks)

#ログイン状態であれば、タスク作成画面へ遷移してDBにタスクを追加する
@tasks_bp.route("/tasks/create", methods=["GET", "POST"])
def task_create():
    if "user_id" not in session:
        flash("ログインが必要です。", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        start_date = request.form.get("start_date", "")
        end_date = request.form.get("end_date", "")
        start_time = request.form.get("start_time", "")
        end_time = request.form.get("end_time", "")

        if start_date and end_date and start_date > end_date:
            flash("開始日は終了日以前にしてください。", "error")
            return render_template("tasks/create.html")

        if start_date == end_date and start_time and end_time:
            flash("開始時間は終了時間以前にしてください。", "error")
            return render_template("tasks/create.html")

        if not title:
            flash("タイトルは必須です。", "error")
            return render_template("tasks/create.html")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        db = get_db()
        db.execute(
            """
            INSERT INTO tasks (user_id, title, description, start_date, end_date, start_time, end_time, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (session["user_id"], title, description, start_date, end_date, start_time, end_time, now, now)
        )
        db.commit()

        flash("タスクを作成しました。", "success")
        return redirect(url_for("tasks.task_list"))

    return render_template("tasks/create.html")

#タスク一覧からタスクの詳細画面へ遷移する
@tasks_bp.route("/tasks/<int:task_id>")
def task_detail(task_id):
    if "user_id" not in session:
        flash("ログインしてください", "error")
        return redirect(url_for("auth.login"))

    db = get_db()
    task = db.execute(
        """
        SELECT id, user_id, title, description, start_date, end_date, start_time, end_time, status, created_at, updated_at
        FROM tasks
        WHERE id = ? AND user_id = ?
        """,
        (task_id, session["user_id"])
    ).fetchone()

    if task is None:
        flash("タスクが見つかりません", "error")
        return redirect(url_for("tasks.task_list"))

    return render_template("tasks/detail.html", task=task)

#タスクがあれば、タスク更新画面へ遷移し更新する
@tasks_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def task_edit(task_id):
    if "user_id" not in session:
        flash("ログインしてください", "error")
        return redirect(url_for("auth.login"))

    db = get_db()
    task = db.execute(
        """
        SELECT id, user_id, title, description, start_date, end_date, start_time, end_time, status, created_at, updated_at
        FROM tasks
        WHERE id = ? AND user_id = ?
        """,
        (task_id, session["user_id"])
    ).fetchone()

    if task is None:
        flash("タスクが見つかりません", "error")
        return redirect(url_for("tasks.task_list"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        start_date = request.form.get("start_date", "")
        end_date = request.form.get("end_date", "")
        start_time = request.form.get("start_time", "")
        end_time = request.form.get("end_time", "")

        if start_date and end_date and start_date > end_date:
            flash("開始日は終了日以前にしてください。", "error")
            return render_template("tasks/create.html")

        if start_date == end_date and start_time and end_time:
            flash("開始時間は終了時間以前にしてください。", "error")
            return render_template("tasks/create.html")

        if not title:
            flash("タイトルは必須です。", "error")
            return render_template("tasks/edit.html", task=task)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        db.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, start_date = ?, end_date = ?, start_time = ?, end_time = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
            """,
            (title, description, start_date, end_date, start_time, end_time, now, task_id, session["user_id"])
        )
        db.commit()

        flash("タスクを更新しました。", "success")
        return redirect(url_for("tasks.task_detail", task_id=task_id))

    return render_template("tasks/edit.html", task=task)

#タスクがあれば、対象のタスクを削除する
@tasks_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
def task_delete(task_id):
    if "user_id" not in session:
        flash("ログインしてください", "error")
        return redirect(url_for("auth.login"))

    db = get_db()

    task = db.execute(
        """
        SELECT id
        FROM tasks
        WHERE id = ? AND user_id = ?
        """,
        (task_id, session["user_id"])
    ).fetchone()

    if task is None:
        flash("タスクがありません", "error")
        return redirect(url_for("tasks.task_list"))

    db.execute(
        """
        DELETE FROM tasks
        WHERE id = ? AND user_id = ?
        """,
        (task_id, session["user_id"])
    )
    db.commit()

    flash("タスクを削除しました。", "success")
    return redirect(url_for("tasks.task_list"))

#タスクの状態の切り替え
@tasks_bp.route("/tasks/<int:task_id>/toggle", methods=["POST"])
def task_toggle(task_id):
    if "user_id" not in session:
        flash("ログインしてください", "error")
        return redirect(url_for("auth.login"))

    db = get_db()

    task = db.execute(
        """
        SELECT id, status
        FROM tasks
        WHERE id = ? AND user_id = ?
        """,
        (task_id, session["user_id"])
    ).fetchone()

    if task is None:
        flash("タスクがありません", "error")
        return redirect(url_for("tasks.task_list"))

    new_status = "completed" if task["status"] == "pending" else "pending"

    db.execute(
        """
        UPDATE tasks
        SET status = ?, updated_at = ?
        WHERE id = ? AND user_id = ?
        """,
        (
            new_status,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            task_id,
            session["user_id"]
        )
    )
    db.commit()

    flash("タスクの状態を変更しました", "success")
    return redirect(url_for("tasks.task_list"))