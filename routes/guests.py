from flask import Blueprint, jsonify, request
from db import get_db, now_time, today

guests_bp = Blueprint("guests", __name__, url_prefix="/api/guests")


@guests_bp.route("", methods=["POST"])
def add_guest():
    data = request.json or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Name required"}), 400

    conn = get_db(); cur = conn.cursor()
    cur.execute(
        "INSERT INTO guest_passes (guest_name,issued_time,issued_date) VALUES (%s,%s,%s)",
        (name, now_time(), today())
    )
    cur.execute(
        "INSERT INTO activity_log (dot,badge,badge_class,text,log_time,log_date) VALUES (%s,%s,%s,%s,%s,%s)",
        ("dot-gray", "Guest pass", "badge-guest",
         f"{name} — walk-in guest pass issued", now_time(), today())
    )
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})
