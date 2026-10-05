import sqlite3


db = sqlite3.connect("data.db", check_same_thread=False)
cur = db.cursor()

def init_db():
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tickets(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        question TEXT,
        group_msg_id INTEGER,
        status TEXT DEFAULT 'open'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS replies(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER,
        author_id INTEGER,
        author_name TEXT,
        text TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bans(
        user_id INTEGER PRIMARY KEY,
        reason TEXT
    )
    """)

    db.commit()


def create_ticket(user, text):
    cur.execute("""
        INSERT INTO tickets(
            user_id,
            username,
            question
        )
        VALUES(?,?,?)
    """, (
        user.id,
        user.username,
        text
    ))

    db.commit()

    return cur.lastrowid


def set_group_message(ticket_id, msg_id):
    cur.execute("""
        UPDATE tickets
        SET group_msg_id=?
        WHERE id=?
    """, (
        msg_id,
        ticket_id
    ))

    db.commit()


def ticket_by_group_message(msg_id):
    row = cur.execute("""
        SELECT id
        FROM tickets
        WHERE group_msg_id=?
    """, (
        msg_id,
    )).fetchone()

    return row[0] if row else None


def close_ticket(ticket_id):
    cur.execute("""
        UPDATE tickets
        SET status='closed'
        WHERE id=?
    """, (
        ticket_id,
    ))

    db.commit()


def ban_user(user_id, reason):
    cur.execute("""
        INSERT OR REPLACE INTO bans(
            user_id,
            reason
        )
        VALUES(?,?)
    """, (
        user_id,
        reason
    ))

    db.commit()


def is_banned(user_id):
    row = cur.execute("""
        SELECT 1
        FROM bans
        WHERE user_id=?
    """, (
        user_id,
    )).fetchone()

    return row is not None

def get_ticket_user(ticket_id):
    row = cur.execute("""
        SELECT user_id
        FROM tickets
        WHERE id=?
    """, (
        ticket_id,
    )).fetchone()
    return row[0] if row else None

def delete_ticket(ticket_id):
    cur.execute("""
        DELETE FROM replies
        WHERE ticket_id=?
    """, (
        ticket_id,
    ))
    cur.execute("""
        DELETE FROM tickets
        WHERE id=?
    """, (
        ticket_id, ))
db.commit()

def is_ticket_open(ticket_id):
    row = cur.execute("""
        SELECT status
        FROM tickets
        WHERE id=?
    """, (
        ticket_id,
    )).fetchone()

    return row is not None and row[0] == "open"

def get_ticket(ticket_id):
    return cur.execute("""
        SELECT user_id, username, question, status
        FROM tickets
        WHERE id=?
    """, (
        ticket_id,
    )).fetchone()

def get_ticket_replies(ticket_id):
    return cur.execute("""
        SELECT author_name, text
        FROM replies
        WHERE ticket_id=?
        ORDER BY id ASC
    """, (
        ticket_id,
    )).fetchall()
