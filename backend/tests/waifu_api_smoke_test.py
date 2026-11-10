"""Run against a running Flask server: python tools/waifu_api_smoke_test.py"""
import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("OTAKUVERSE_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
COOKIE = None

def request(path, method="GET", body=None):
    global COOKIE
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if COOKIE:
        headers["Cookie"] = COOKIE
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            cookie = response.headers.get("Set-Cookie")
            if cookie:
                COOKIE = cookie.split(";", 1)[0]
            raw = response.read().decode("utf-8")
            try:
                return response.status, json.loads(raw)
            except json.JSONDecodeError:
                return response.status, {"_non_json": raw[:500]}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"_non_json": raw[:500]}
    except Exception as exc:
        return None, {"error": str(exc)}

def check(name, path, expected=(200,)):
    status, payload = request(path)
    ok = status in expected
    print(("PASS" if ok else "FAIL"), name, "HTTP", status, payload)
    return ok

def main():
    print("Testing", BASE)
    results = []
    results.append(check("Flask root responds", "/", expected=(200, 301, 302, 404)))
    results.append(check("Waifu result route is registered", "/api/waifu/result/", expected=(401, 400, 409, 200)))
    status, payload = request("/api/waifu/profile/start", "POST", {})
    started = status in (200, 201) and isinstance(payload, dict) and payload.get("success") is True
    print(("PASS" if started else "FAIL"), "Start questionnaire", "HTTP", status, payload)
    results.append(started)
    if started:
        question = payload.get("question")
        if question is None:
            print("WARN No next question returned. Check that approved questions exist for both profile types.")
        else:
            print("INFO First question fields:", sorted(question.keys()))
            options = question.get("options") or []
            if not options:
                print("WARN Question has no answer options.")
            for index, option in enumerate(options):
                if not isinstance(option, dict):
                    continue
                media = option.get("media") or {}
                print("INFO option", index + 1, "media fields:", sorted(media.keys()))
            media = question.get("media") or {}
            print("INFO question media fields:", sorted(media.keys()))
    print("\nResult:", sum(bool(x) for x in results), "/", len(results), "checks passed.")
    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main())
