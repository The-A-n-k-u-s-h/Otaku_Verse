
from werkzeug.security import generate_password_hash, check_password_hash
from app.services.waifu_database import get_db

ROLES = {"super_admin", "question_manager", "reviewer", "content_manager"}
PERMISSIONS = {
    "super_admin": {"questions", "review", "characters", "json", "operators", "schedule", "media"},
    "question_manager": {"questions", "json", "schedule", "media"},
    "reviewer": {"review"},
    "content_manager": {"characters", "media"},
}

def authenticate(username, password):
    row = get_db().execute("SELECT * FROM waifu_operator_accounts WHERE username=? AND is_active=1",
                           (username,)).fetchone()
    if not row or not check_password_hash(row["password_hash"], password):
        return None
    return dict(row)

def create_operator(username, password, role):
    username = str(username or "").strip()
    if len(username) < 3: raise ValueError("Username must contain at least 3 characters.")
    if len(password or "") < 12: raise ValueError("Password must contain at least 12 characters.")
    if role not in ROLES: raise ValueError("Invalid operator role.")
    db = get_db()
    if db.execute("SELECT 1 FROM waifu_operator_accounts WHERE username=?", (username,)).fetchone():
        raise ValueError("That username already exists.")
    cur = db.execute("INSERT INTO waifu_operator_accounts(username,password_hash,role) VALUES(?,?,?)",
                     (username, generate_password_hash(password), role))
    db.commit()
    return cur.lastrowid

def list_operators():
    return [dict(row) for row in get_db().execute(
        "SELECT id,username,role,is_active,created_at FROM waifu_operator_accounts ORDER BY id")]

def set_operator_active(operator_id, active):
    db=get_db()
    cur=db.execute("UPDATE waifu_operator_accounts SET is_active=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                   (1 if active else 0, operator_id))
    db.commit()
    return cur.rowcount > 0

def has_operator_accounts():
    return get_db().execute("SELECT 1 FROM waifu_operator_accounts LIMIT 1").fetchone() is not None
