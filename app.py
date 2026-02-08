from flask import Flask, redirect, render_template, request, url_for
import sqlite3
from pathlib import Path

APP_ROOT = Path(__file__).parent
DATABASE_PATH = APP_ROOT / "owners.db"

app = Flask(__name__)


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS owners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number TEXT NOT NULL,
                owner_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


@app.route("/")
def index():
    with get_connection() as connection:
        owners = connection.execute(
            "SELECT * FROM owners ORDER BY id DESC"
        ).fetchall()
    return render_template("index.html", owners=owners)


@app.post("/create")
def create_owner():
    room_number = request.form.get("room_number", "").strip()
    owner_name = request.form.get("owner_name", "").strip()
    phone = request.form.get("phone", "").strip()

    if not room_number or not owner_name or not phone:
        return redirect(url_for("index"))

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO owners (room_number, owner_name, phone, created_at)
            VALUES (?, ?, ?, datetime('now', 'localtime'))
            """,
            (room_number, owner_name, phone),
        )
    return redirect(url_for("index"))


@app.route("/edit/<int:owner_id>")
def edit_owner(owner_id):
    with get_connection() as connection:
        owner = connection.execute(
            "SELECT * FROM owners WHERE id = ?",
            (owner_id,),
        ).fetchone()
    if owner is None:
        return redirect(url_for("index"))
    return render_template("edit.html", owner=owner)


@app.post("/update/<int:owner_id>")
def update_owner(owner_id):
    room_number = request.form.get("room_number", "").strip()
    owner_name = request.form.get("owner_name", "").strip()
    phone = request.form.get("phone", "").strip()

    if not room_number or not owner_name or not phone:
        return redirect(url_for("edit_owner", owner_id=owner_id))

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE owners
            SET room_number = ?, owner_name = ?, phone = ?
            WHERE id = ?
            """,
            (room_number, owner_name, phone, owner_id),
        )
    return redirect(url_for("index"))


@app.post("/delete/<int:owner_id>")
def delete_owner(owner_id):
    with get_connection() as connection:
        connection.execute("DELETE FROM owners WHERE id = ?", (owner_id,))
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
