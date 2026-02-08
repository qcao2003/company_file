from flask import Flask, redirect, render_template, request, url_for
from pathlib import Path
import sqlite3

APP_ROOT = Path(__file__).parent
DATABASE_PATH = APP_ROOT / "owners.db"

app = Flask(__name__)


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def ensure_column(connection, column_name, column_type, default_value=None):
    existing_columns = {
        row["name"] for row in connection.execute("PRAGMA table_info(owners)")
    }
    if column_name in existing_columns:
        return
    default_clause = f" DEFAULT {default_value}" if default_value is not None else ""
    connection.execute(
        f"ALTER TABLE owners ADD COLUMN {column_name} {column_type}{default_clause}"
    )


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS owners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number TEXT NOT NULL,
                owner_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                age INTEGER NOT NULL DEFAULT 0,
                property_fee REAL NOT NULL DEFAULT 0,
                arrears REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )
        ensure_column(connection, "age", "INTEGER", 0)
        ensure_column(connection, "property_fee", "REAL", 0)
        ensure_column(connection, "arrears", "REAL", 0)


@app.route("/")
def index():
    with get_connection() as connection:
        owners = connection.execute(
            "SELECT * FROM owners ORDER BY id DESC"
        ).fetchall()
        total_count = connection.execute(
            "SELECT COUNT(*) AS count FROM owners"
        ).fetchone()["count"]
        with_arrears = connection.execute(
            "SELECT COUNT(*) AS count FROM owners WHERE arrears > 0"
        ).fetchone()["count"]
        total_arrears = connection.execute(
            "SELECT COALESCE(SUM(arrears), 0) AS total FROM owners"
        ).fetchone()["total"]
        total_property_fee = connection.execute(
            "SELECT COALESCE(SUM(property_fee), 0) AS total FROM owners"
        ).fetchone()["total"]
        age_rows = connection.execute(
            """
            SELECT
                SUM(CASE WHEN age BETWEEN 0 AND 30 THEN 1 ELSE 0 END) AS age_0_30,
                SUM(CASE WHEN age BETWEEN 31 AND 45 THEN 1 ELSE 0 END) AS age_31_45,
                SUM(CASE WHEN age BETWEEN 46 AND 60 THEN 1 ELSE 0 END) AS age_46_60,
                SUM(CASE WHEN age >= 61 THEN 1 ELSE 0 END) AS age_61_plus
            FROM owners
            """
        ).fetchone()
    age_distribution = {
        "0-30岁": age_rows["age_0_30"],
        "31-45岁": age_rows["age_31_45"],
        "46-60岁": age_rows["age_46_60"],
        "61岁以上": age_rows["age_61_plus"],
    }
    return render_template(
        "index.html",
        owners=owners,
        total_count=total_count,
        with_arrears=with_arrears,
        total_arrears=total_arrears,
        total_property_fee=total_property_fee,
        age_distribution=age_distribution,
    )


@app.post("/create")
def create_owner():
    room_number = request.form.get("room_number", "").strip()
    owner_name = request.form.get("owner_name", "").strip()
    phone = request.form.get("phone", "").strip()
    age = request.form.get("age", "0").strip()
    property_fee = request.form.get("property_fee", "0").strip()
    arrears = request.form.get("arrears", "0").strip()

    if not room_number or not owner_name or not phone:
        return redirect(url_for("index"))

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO owners (room_number, owner_name, phone, age, property_fee, arrears, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
            """,
            (room_number, owner_name, phone, int(age or 0), float(property_fee or 0), float(arrears or 0)),
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
    age = request.form.get("age", "0").strip()
    property_fee = request.form.get("property_fee", "0").strip()
    arrears = request.form.get("arrears", "0").strip()

    if not room_number or not owner_name or not phone:
        return redirect(url_for("edit_owner", owner_id=owner_id))

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE owners
            SET room_number = ?, owner_name = ?, phone = ?, age = ?, property_fee = ?, arrears = ?
            WHERE id = ?
            """,
            (room_number, owner_name, phone, int(age or 0), float(property_fee or 0), float(arrears or 0), owner_id),
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
