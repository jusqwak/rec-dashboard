from flask import Blueprint, jsonify
from db import get_db, serialize, rows_as_dicts, today

stats_bp = Blueprint("stats", __name__, url_prefix="/api")


@stats_bp.route("/stats")
def get_stats():
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM members WHERE status='in'")
    inside = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM activity_log WHERE badge='Check-in' AND log_date=%s", (today(),))
    checkins = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM guest_passes WHERE issued_date=%s", (today(),))
    guests = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bookings WHERE booking_date=%s", (today(),))
    bookings = cur.fetchone()[0]
    cur.close(); conn.close()
    return jsonify({"inside": inside, "checkins": checkins, "guests": guests, "bookings": bookings})


@stats_bp.route("/log")
def get_log():
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM activity_log ORDER BY log_id DESC LIMIT 200")
    rows = serialize(rows_as_dicts(cur))
    cur.close(); conn.close()
    return jsonify(rows)
