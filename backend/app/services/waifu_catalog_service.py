import json
from app.services.waifu_database import get_db
from app.utils.waifu_validation import (
    clean_text, safe_slug, validate_http_url, validate_traits, validate_options,
    ALL_TRAITS, STATUSES
)

def _character_dict(row):
    data = dict(row)
    db = get_db()
    traits = db.execute(
        "SELECT profile_type, trait_key, trait_label, score FROM character_traits WHERE character_id=? ORDER BY profile_type, trait_key",
        (data["id"],)
    ).fetchall()
    data["traits"] = {"personality": {}, "romantic": {}}
    for trait in traits:
        data["traits"][trait["profile_type"]][trait["trait_key"]] = {
            "label": trait["trait_label"], "score": trait["score"]
        }
    data["sources"] = [dict(x) for x in db.execute(
        "SELECT * FROM character_sources WHERE character_id=? ORDER BY id", (data["id"],)
    ).fetchall()]
    return data

def list_characters(status=None, search=None, page=1, per_page=20, approved_only=False):
    db = get_db()
    clauses, params = [], []
    if approved_only:
        clauses.append("status='approved'")
    elif status in STATUSES:
        clauses.append("status=?"); params.append(status)
    if search:
        clauses.append("(name LIKE ? OR anime_title LIKE ? OR aliases LIKE ?)")
        term = f"%{search.strip()}%"
        params.extend([term, term, term])
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    total = db.execute("SELECT COUNT(*) FROM waifu_characters" + where, params).fetchone()[0]
    page = max(1, int(page)); per_page = min(100, max(1, int(per_page)))
    rows = db.execute(
        "SELECT * FROM waifu_characters" + where + " ORDER BY updated_at DESC, id DESC LIMIT ? OFFSET ?",
        (*params, per_page, (page-1)*per_page)
    ).fetchall()
    return {"items": [_character_dict(r) for r in rows], "total": total, "page": page, "per_page": per_page}

def get_character(character_id):
    row = get_db().execute("SELECT * FROM waifu_characters WHERE id=?", (character_id,)).fetchone()
    return _character_dict(row) if row else None

def create_character(data, actor="operator"):
    db = get_db()
    name = clean_text(data.get("name"), "Character name", 150, True)
    anime = clean_text(data.get("anime_title"), "Anime title", 200, True)
    traits = validate_traits(data.get("traits", {}))
    slug_base = safe_slug(f"{name}-{anime}")
    slug, suffix = slug_base, 2
    while db.execute("SELECT 1 FROM waifu_characters WHERE slug=?", (slug,)).fetchone():
        slug = f"{slug_base}-{suffix}"; suffix += 1
    image_url = validate_http_url(data.get("image_url"), "Image URL")
    image_source = validate_http_url(data.get("image_source_url"), "Image source URL")
    sources = data.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("Sources must be a list.")
    cur = db.execute("""
        INSERT INTO waifu_characters
        (name,slug,anime_title,aliases,description,biography,image_url,image_source_url,status,verification_status,created_by)
        VALUES (?,?,?,?,?,?,?,?, 'draft','unverified',?)
    """, (name, slug, anime, clean_text(data.get("aliases"), "Aliases", 500),
          clean_text(data.get("description"), "Description", 1000),
          clean_text(data.get("biography"), "Biography", 5000),
          image_url, image_source, actor))
    cid = cur.lastrowid
    _save_character_traits(db, cid, traits)
    _save_sources(db, cid, sources)
    db.commit()
    return get_character(cid)

def update_character(character_id, data):
    db = get_db()
    existing = get_character(character_id)
    if not existing:
        return None
    name = clean_text(data.get("name", existing["name"]), "Character name", 150, True)
    anime = clean_text(data.get("anime_title", existing["anime_title"]), "Anime title", 200, True)
    traits = validate_traits(data.get("traits", {
        p: {k:v["score"] for k,v in existing["traits"][p].items()} for p in ("personality","romantic")
    }))
    db.execute("""
        UPDATE waifu_characters SET name=?, anime_title=?, aliases=?, description=?, biography=?,
        image_url=?, image_source_url=?, verification_status='unverified', status='draft',
        reviewed_by=NULL, reviewed_at=NULL, rejection_reason=NULL, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (name, anime,
          clean_text(data.get("aliases", existing["aliases"]), "Aliases", 500),
          clean_text(data.get("description", existing["description"]), "Description", 1000),
          clean_text(data.get("biography", existing["biography"]), "Biography", 5000),
          validate_http_url(data.get("image_url", existing["image_url"]), "Image URL"),
          validate_http_url(data.get("image_source_url", existing["image_source_url"]), "Image source URL"),
          character_id))
    db.execute("DELETE FROM character_traits WHERE character_id=?", (character_id,))
    _save_character_traits(db, character_id, traits)
    if "sources" in data:
        db.execute("DELETE FROM character_sources WHERE character_id=?", (character_id,))
        _save_sources(db, character_id, data["sources"])
    db.commit()
    return get_character(character_id)

def _save_character_traits(db, cid, traits):
    from app.utils.waifu_validation import ALL_TRAITS
    for profile_type, values in traits.items():
        for key, score in values.items():
            db.execute(
                "INSERT INTO character_traits(character_id,profile_type,trait_key,trait_label,score) VALUES(?,?,?,?,?)",
                (cid, profile_type, key, ALL_TRAITS[profile_type][key], score)
            )

def _save_sources(db, cid, sources):
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("Each source must be an object.")
        name = clean_text(source.get("name"), "Source name", 150, True)
        url = validate_http_url(source.get("url"), "Source URL", True)
        db.execute(
            "INSERT INTO character_sources(character_id,source_name,source_url,source_type,notes,verified) VALUES(?,?,?,?,?,?)",
            (cid, name, url, clean_text(source.get("type","reference"), "Source type", 50),
             clean_text(source.get("notes"), "Source notes", 1000),
             1 if source.get("verified") else 0)
        )

def set_character_status(character_id, status, actor, reason=""):
    if status not in STATUSES:
        raise ValueError("Invalid character status.")
    db = get_db()
    row = db.execute("SELECT id FROM waifu_characters WHERE id=?", (character_id,)).fetchone()
    if not row:
        return False
    if status == "approved":
        character = get_character(character_id)
        if not character["name"] or not character["anime_title"]:
            raise ValueError("Character name and anime title are required.")
        if not character["traits"]["personality"] or not character["traits"]["romantic"]:
            raise ValueError("Add at least one personality trait and one romantic trait before approval.")
        if not character["sources"]:
            raise ValueError("Add at least one source before approval.")
        if not any(s["verified"] for s in character["sources"]):
            raise ValueError("At least one source must be marked verified before approval.")
        if not character["image_url"] or not character["image_source_url"]:
            raise ValueError("An image URL and image source URL are required before approval.")
        db.execute("UPDATE waifu_characters SET verification_status='verified' WHERE id=?", (character_id,))
    db.execute("""
        UPDATE waifu_characters SET status=?, reviewed_by=?, reviewed_at=CURRENT_TIMESTAMP,
        rejection_reason=?, updated_at=CURRENT_TIMESTAMP WHERE id=?
    """, (status, actor, clean_text(reason, "Reason", 1000), character_id))
    db.commit()
    return True

def delete_character(character_id):
    db = get_db()
    cur = db.execute("DELETE FROM waifu_characters WHERE id=?", (character_id,))
    db.commit()
    return cur.rowcount > 0

def list_questions(status=None, search=None, approved_only=False):
    db = get_db()
    clauses, params = [], []
    if approved_only:
        clauses.append("q.status='approved'")
    elif status in STATUSES:
        clauses.append("q.status=?"); params.append(status)
    if search:
        clauses.append("q.prompt LIKE ?"); params.append(f"%{search.strip()}%")
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    rows = db.execute("""
        SELECT q.* FROM matching_questions q
    """ + where + " ORDER BY q.display_order, q.id", params).fetchall()
    result=[]
    for row in rows:
        item=dict(row)
        item["options"]=[]
        opts=db.execute("SELECT * FROM question_options WHERE question_id=? ORDER BY display_order,id",(item["id"],)).fetchall()
        for opt in opts:
            o=dict(opt)
            o["mappings"]=[dict(x) for x in db.execute("SELECT trait_key,score_value FROM question_trait_mappings WHERE option_id=?",(o["id"],)).fetchall()]
            item["options"].append(o)
        result.append(item)
    return result

def get_question(question_id):
    return next((q for q in list_questions() if q["id"] == question_id), None)

def create_question(data, actor="operator"):
    db=get_db()
    prompt=clean_text(data.get("prompt"),"Question",500,True)
    category=clean_text(data.get("category"),"Category",80,True)
    profile_type=data.get("profile_type")
    if profile_type not in ("personality","romantic"):
        raise ValueError("Profile type must be personality or romantic.")
    trait_key=clean_text(data.get("trait_key"),"Trait",80,True)
    if trait_key not in ALL_TRAITS[profile_type]:
        raise ValueError("Unknown trait for selected profile type.")
    options=validate_options(data.get("options"))
    cur=db.execute("""
        INSERT INTO matching_questions(prompt,category,profile_type,trait_key,explanation,status,is_required,display_order,created_by)
        VALUES(?,?,?,?,?,'draft',?,?,?)
    """,(prompt,category,profile_type,trait_key,clean_text(data.get("explanation"),"Explanation",1000),
         1 if data.get("is_required",True) else 0,int(data.get("display_order",0)),actor))
    qid=cur.lastrowid
    for option in options:
        cur2=db.execute("INSERT INTO question_options(question_id,option_text,display_order) VALUES(?,?,?)",
                        (qid,option["text"],option["order"]))
        db.execute("INSERT INTO question_trait_mappings(option_id,trait_key,score_value) VALUES(?,?,?)",
                   (cur2.lastrowid,trait_key,option["score"]))
    db.commit()
    return get_question(qid)

def update_question(question_id,data):
    db=get_db()
    existing=get_question(question_id)
    if not existing: return None
    prompt=clean_text(data.get("prompt",existing["prompt"]),"Question",500,True)
    category=clean_text(data.get("category",existing["category"]),"Category",80,True)
    profile_type=data.get("profile_type",existing["profile_type"])
    trait_key=data.get("trait_key",existing["trait_key"])
    if profile_type not in ALL_TRAITS or trait_key not in ALL_TRAITS[profile_type]:
        raise ValueError("Unknown trait for selected profile type.")
    options=validate_options(data.get("options", [{"text":o["option_text"],"score":next((m["score_value"] for m in o["mappings"] if m["trait_key"]==trait_key),50)} for o in existing["options"]]))
    db.execute("""
        UPDATE matching_questions SET prompt=?,category=?,profile_type=?,trait_key=?,explanation=?,
        is_required=?,display_order=?,status='draft',reviewed_by=NULL,reviewed_at=NULL,rejection_reason=NULL,
        updated_at=CURRENT_TIMESTAMP WHERE id=?
    """,(prompt,category,profile_type,trait_key,
         clean_text(data.get("explanation",existing["explanation"]),"Explanation",1000),
         1 if data.get("is_required",existing["is_required"]) else 0,
         int(data.get("display_order",existing["display_order"])),question_id))
    db.execute("DELETE FROM question_options WHERE question_id=?",(question_id,))
    for option in options:
        cur=db.execute("INSERT INTO question_options(question_id,option_text,display_order) VALUES(?,?,?)",
                       (question_id,option["text"],option["order"]))
        db.execute("INSERT INTO question_trait_mappings(option_id,trait_key,score_value) VALUES(?,?,?)",
                   (cur.lastrowid,trait_key,option["score"]))
    db.commit()
    return get_question(question_id)

def set_question_status(question_id,status,actor,reason=""):
    if status not in STATUSES: raise ValueError("Invalid question status.")
    db=get_db()
    q=get_question(question_id)
    if not q: return False
    if status=="approved":
        if len(q["options"])<2: raise ValueError("A question needs at least two answer options.")
        if any(not o["mappings"] for o in q["options"]):
            raise ValueError("Every answer option needs a scoring mapping.")
    db.execute("""
        UPDATE matching_questions SET status=?,reviewed_by=?,reviewed_at=CURRENT_TIMESTAMP,
        rejection_reason=?,updated_at=CURRENT_TIMESTAMP WHERE id=?
    """,(status,actor,clean_text(reason,"Reason",1000),question_id))
    db.commit()
    return True

def delete_question(question_id):
    db=get_db()
    cur=db.execute("DELETE FROM matching_questions WHERE id=?",(question_id,))
    db.commit()
    return cur.rowcount>0
