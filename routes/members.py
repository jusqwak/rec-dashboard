from flask import Blueprint, jsonify, request
from config import AVATAR_COLORS, random_avatar_color
from db import get_db, next_member_id, row_as_dict, rows_as_dicts, today, now_time

members_bp = Blueprint("members", __name__, url_prefix="/api/members")


@members_bp.route("")
def get_members():
    q = "%" + request.args.get("q", "").lower() + "%"
    conn = get_db(); cur = conn.cursor()
    cur.execute(
        "SELECT * FROM members WHERE LOWER(name) LIKE %s OR LOWER(id) LIKE %s",
        (q, q)
    )
    rows = rows_as_dicts(cur)
    cur.close(); conn.close()
    return jsonify(rows)


@members_bp.route("/<member_id>/checkin", methods=["POST"])
def checkin(member_id):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM members WHERE id=%s", (member_id,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close()
        return jsonify({"error": "Member not found"}), 404
    m = row_as_dict(cur, row)
    if m["status"] == "in":
        cur.close(); conn.close()
        return jsonify({"error": f"{m['name']} is already checked in"}), 409

    cur.execute("UPDATE members SET status='in' WHERE id=%s", (member_id,))
    cur.execute(
        "INSERT INTO activity_log (dot,badge,badge_class,text,log_time,log_date) VALUES (%s,%s,%s,%s,%s,%s)",
        ("dot-green", "Check-in", "badge-checkin",
         f"{m['name']} ({m['id']}) — {m['type']} member", now_time(), today())
    )
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True, "name": m["name"]})


@members_bp.route("/<member_id>/checkout", methods=["POST"])
def checkout(member_id):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM members WHERE id=%s", (member_id,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close()
        return jsonify({"error": "Member not found"}), 404
    m = row_as_dict(cur, row)
    if m["status"] == "out":
        cur.close(); conn.close()
        return jsonify({"error": f"{m['name']} is not currently checked in"}), 409

    cur.execute("UPDATE members SET status='out' WHERE id=%s", (member_id,))
    cur.execute(
        "INSERT INTO activity_log (dot,badge,badge_class,text,log_time,log_date) VALUES (%s,%s,%s,%s,%s,%s)",
        ("dot-amber", "Check-out", "badge-checkout",
         f"{m['name']} ({m['id']}) checked out", now_time(), today())
    )
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True, "name": m["name"]})


@members_bp.route("", methods=["POST"])
def create_member():
    data = request.json or {}
    name = (data.get("name") or "").strip()
    type_ = (data.get("type") or "").strip()
    initials = (data.get("initials") or "").strip()
    color = (data.get("color_class") or "").strip()
    status = (data.get("status") or "out").strip().lower()
    if status not in ("in", "out"):
        status = "out"
    if not (name and type_ and initials):
        return jsonify({"error": "All member fields are required"}), 400
    if color not in AVATAR_COLORS:
        color = random_avatar_color()

    conn = get_db()
    member_id = next_member_id(conn)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO members (id,name,type,initials,color_class,status) VALUES (%s,%s,%s,%s,%s,%s)",
        (member_id, name, type_, initials, color, status)
    )
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True, "id": member_id})


@members_bp.route("/<member_id>", methods=["PUT"])
def update_member(member_id):
    data = request.json or {}
    updates = {}
    for key in ("name", "type", "initials", "color_class", "status"):
        if key in data and data[key] is not None:
            value = str(data[key]).strip()
            if key == "status":
                value = value.lower()
                if value not in ("in", "out"):
                    continue
            if value:
                updates[key] = value

    if not updates:
        return jsonify({"error": "No update fields provided"}), 400

    fields = ", ".join(f"{k}=%s" for k in updates)
    values = list(updates.values()) + [member_id]

    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT 1 FROM members WHERE id=%s", (member_id,))
    if not cur.fetchone():
        cur.close(); conn.close()
        return jsonify({"error": "Member not found"}), 404

    cur.execute(f"UPDATE members SET {fields} WHERE id=%s", tuple(values))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})


@members_bp.route("/<member_id>", methods=["DELETE"])
def delete_member(member_id):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT name FROM members WHERE id=%s", (member_id,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close()
        return jsonify({"error": "Member not found"}), 404

    name = row[0]
    cur.execute("DELETE FROM members WHERE id=%s", (member_id,))
    cur.execute(
        "INSERT INTO activity_log (dot,badge,badge_class,text,log_time,log_date) VALUES (%s,%s,%s,%s,%s,%s)",
        ("dot-gray", "Member removed", "badge-remove",
         f"{name} ({member_id}) was removed", now_time(), today())
    )
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})
