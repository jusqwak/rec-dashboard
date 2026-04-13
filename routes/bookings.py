from flask import Blueprint, jsonify, request
from db import get_db, serialize, rows_as_dicts, today, now_time

bookings_bp = Blueprint("bookings", __name__, url_prefix="/api/bookings")


@bookings_bp.route("")
def get_bookings():
    conn = get_db(); cur = conn.cursor()
    cur.execute(
        "SELECT * FROM bookings WHERE booking_date=%s ORDER BY booking_id DESC",
        (today(),)
    )
    rows = serialize(rows_as_dicts(cur))
    cur.close(); conn.close()
    return jsonify(rows)


@bookings_bp.route("", methods=["POST"])
def add_booking():
    data = request.json or {}
    facility = (data.get("facility") or "").strip()
    time_slot = (data.get("time_slot") or "").strip()
    member_name = (data.get("member_name") or "").strip()
    if not (facility and time_slot and member_name):
        return jsonify({"error": "All fields required"}), 400

    conn = get_db(); cur = conn.cursor()
    cur.execute(
        "INSERT INTO bookings (facility,time_slot,member_name,booking_date) VALUES (%s,%s,%s,%s)",
        (facility, time_slot, member_name, today())
    )
    cur.execute(
        "INSERT INTO activity_log (dot,badge,badge_class,text,log_time,log_date) VALUES (%s,%s,%s,%s,%s,%s)",
        ("dot-purple", "Booking", "badge-booking",
         f"{facility} booked for {member_name} at {time_slot}", now_time(), today())
    )
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})


@bookings_bp.route("/<int:booking_id>", methods=["DELETE"])
def delete_booking(booking_id):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT facility, member_name, time_slot FROM bookings WHERE booking_id=%s", (booking_id,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close()
        return jsonify({"error": "Booking not found"}), 404

    facility, member_name, time_slot = row
    cur.execute("DELETE FROM bookings WHERE booking_id=%s", (booking_id,))
    cur.execute(
        "INSERT INTO activity_log (dot,badge,badge_class,text,log_time,log_date) VALUES (%s,%s,%s,%s,%s,%s)",
        ("dot-purple", "Booking", "badge-booking",
         f"{facility} booking for {member_name} canceled", now_time(), today())
    )
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})
