import json
import urllib.request
from datetime import datetime, timezone

ALLOWED_MEDIA_TYPES = {"image", "gif", "audio"}

def check_media_url(url, media_type, timeout=8):
    """Check an external media URL without downloading the full asset."""
    if media_type not in ALLOWED_MEDIA_TYPES:
        raise ValueError("Unsupported media type.")
    if not url:
        return {"ok": True, "status": "empty", "message": "No URL supplied."}
    if not isinstance(url, str) or not url.startswith(("https://", "http://")):
        return {"ok": False, "status": "invalid_url", "message": "Only HTTP(S) URLs are supported."}
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "OtakuVerse-Media-Checker/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get("Content-Type", "").lower()
            valid = (
                (media_type == "image" and content_type.startswith("image/")) or
                (media_type == "gif" and ("image/gif" in content_type or content_type.startswith("image/"))) or
                (media_type == "audio" and content_type.startswith("audio/"))
            )
            return {
                "ok": response.status < 400 and valid,
                "status": response.status,
                "content_type": content_type,
                "message": "Media URL is reachable." if valid else "URL responded, but content type may not match the selected media type."
            }
    except Exception as exc:
        return {"ok": False, "status": "unreachable", "message": str(exc)[:300]}

def schedule_is_active(start_at=None, end_at=None, now=None):
    now = now or datetime.now(timezone.utc)
    def parse(value):
        if not value:
            return None
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    start, end = parse(start_at), parse(end_at)
    return (start is None or now >= start) and (end is None or now <= end)

def validate_schedule(start_at=None, end_at=None):
    start = datetime.fromisoformat(start_at.replace("Z", "+00:00")) if start_at else None
    end = datetime.fromisoformat(end_at.replace("Z", "+00:00")) if end_at else None
    if start and end and end <= start:
        raise ValueError("Schedule end must be later than schedule start.")
    return True
