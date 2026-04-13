import mysql.connector
from datetime import date, datetime
from config import DB_CONFIG


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def next_member_id(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM members")
    rows = [row[0] for row in cur.fetchall()]
    cur.close()
    used = set(rows)
    for num in range(1, 10000):
        candidate = f"M-{num:04d}"
        if candidate not in used:
            return candidate
    return f"M-{len(used) + 1:04d}"


def init_db():
    cfg_no_db = {k: v for k, v in DB_CONFIG.items() if k != "database"}
    conn = mysql.connector.connect(**cfg_no_db)
    cur = conn.cursor()

    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`")
    cur.execute(f"USE `{DB_CONFIG['database']}`")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id          VARCHAR(20)  PRIMARY KEY,
            name        VARCHAR(120) NOT NULL,
            type        VARCHAR(60)  NOT NULL,
            initials    VARCHAR(4)   NOT NULL,
            color_class VARCHAR(20)  NOT NULL,
            status      VARCHAR(10)  NOT NULL DEFAULT 'out'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            log_id      INT AUTO_INCREMENT PRIMARY KEY,
            dot         VARCHAR(30)  NOT NULL,
            badge       VARCHAR(30)  NOT NULL,
            badge_class VARCHAR(30)  NOT NULL,
            text        VARCHAR(255) NOT NULL,
            log_time    VARCHAR(20)  NOT NULL,
            log_date    DATE         NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id   INT AUTO_INCREMENT PRIMARY KEY,
            facility     VARCHAR(80)  NOT NULL,
            time_slot    VARCHAR(80)  NOT NULL,
            member_name  VARCHAR(120) NOT NULL,
            booking_date DATE         NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS guest_passes (
            pass_id     INT AUTO_INCREMENT PRIMARY KEY,
            guest_name  VARCHAR(120) NOT NULL,
            issued_time VARCHAR(20)  NOT NULL,
            issued_date DATE         NOT NULL
        )
    """)

    cur.execute("SELECT COUNT(*) FROM members")
    if cur.fetchone()[0] == 0:
        seed = [
            ("M-1042", "Jamie Torres",  "Annual",   "JT", "av-blue",   "out"),
            ("M-0871", "Priya Nair",    "Monthly",  "PN", "av-green",  "out"),
            ("M-2210", "Carlos Webb",   "Annual",   "CW", "av-amber",  "out"),
            ("M-1598", "Sofia Okafor",  "Family",   "SO", "av-purple", "out"),
            ("M-0334", "Alex Kim",      "Monthly",  "AK", "av-blue",   "out"),
            ("M-1777", "Dana Flores",   "Annual",   "DF", "av-green",  "out"),
            ("M-0992", "Marcus Bell",   "Day pass", "MB", "av-amber",  "out"),
            ("M-2045", "Yuki Chen",     "Family",   "YC", "av-purple", "out"),
        ]
        cur.executemany(
            "INSERT INTO members (id,name,type,initials,color_class,status) VALUES (%s,%s,%s,%s,%s,%s)",
            seed
        )

    conn.commit()
    cur.close()
    conn.close()
    print("✅  Database ready.")


def today():
    return str(date.today())


def now_time():
    return datetime.now().strftime("%I:%M %p")


def rows_as_dicts(cursor):
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def row_as_dict(cursor, row):
    cols = [d[0] for d in cursor.description]
    return dict(zip(cols, row))


def serialize(rows):
    for r in rows:
        for k, v in r.items():
            if hasattr(v, "isoformat"):
                r[k] = v.isoformat()
    return rows
