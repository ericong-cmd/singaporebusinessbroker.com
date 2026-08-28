#!/usr/bin/env python3
"""Deploy singaporebusinessbroker.com to Vercel production.

Uploads the SOURCE tree and lets Vercel run the Astro build, so the serverless
functions in api/ are compiled and deployed alongside the static output. Then
promotes to production, attaches the domains and prints the DNS to set.

Requires a Vercel token in env var VERCEL_TOKEN (or `vercel`).
Usage: python3 deploy_vercel.py
"""
import base64
import json
import os
import sys
import time
import subprocess
import tempfile

API = "https://api.vercel.com"
PROJECT = "singaporebusinessbroker"
APEX = "singaporebusinessbroker.com"
WWW = "www." + APEX

# Vercel builds from source, so node_modules and build output stay local.
EXCLUDE_DIRS = {
    ".git", ".github", "node_modules", "dist", ".astro", ".vercel",
    "__pycache__", ".image-cache", "prototype",
}
EXCLUDE_FILES = {".DS_Store", ".env", ".env.local", "deploy_vercel.py"}
MAX_BYTES = 8 * 1024 * 1024

TOKEN = os.environ.get("VERCEL_TOKEN") or os.environ.get("vercel")
if not TOKEN:
    sys.exit("No Vercel token: set VERCEL_TOKEN (or `vercel`) in the environment.")


def api(method, path, body=None, ok_conflict=False):
    """Call the Vercel API.

    Uses curl rather than urllib: in a proxied sandbox, urllib intermittently
    dies with `SSL: UNEXPECTED_EOF_WHILE_READING` partway through the multi-MB
    deployment POST, while curl handles the same proxy and CA bundle fine.
    """
    args = [
        "curl", "-sS", "--max-time", "600",
        "-o", "-", "-w", "\n%{http_code}",
        "-X", method,
        "-H", "Authorization: Bearer " + TOKEN,
        API + path,
    ]
    payload = None
    if body is not None:
        payload = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump(body, payload)
        payload.close()
        args[-1:-1] = ["-H", "Content-Type: application/json", "--data-binary", "@" + payload.name]

    # Transient TLS/connection failures to api.vercel.com are common from a
    # proxied network, and they hit the multi-MB deployment POST hardest.
    # 35/52/56/7/28 are curl's connect, empty-reply, recv-error, no-route and
    # timeout codes: all worth retrying, unlike an auth or payload error.
    RETRYABLE = {7, 28, 35, 52, 56}
    proc = None
    for attempt in range(6):
        try:
            proc = subprocess.run(args, capture_output=True, text=True, timeout=900)
        except subprocess.TimeoutExpired:
            proc = None
        if proc is not None and proc.returncode == 0:
            break
        code = proc.returncode if proc is not None else "timeout"
        if proc is not None and proc.returncode not in RETRYABLE:
            break
        if attempt < 5:
            wait = 2 ** attempt * 5
            print("  %s %s transient failure (%s), retrying in %ss" % (method, path, code, wait))
            time.sleep(wait)

    if payload:
        os.unlink(payload.name)

    if proc is None or proc.returncode != 0:
        rc = proc.returncode if proc is not None else "timeout"
        err = proc.stderr[:400] if proc is not None else ""
        sys.exit("%s %s -> curl failed after retries (%s): %s" % (method, path, rc, err))

    raw, _, status = proc.stdout.rpartition("\n")
    code = int(status.strip() or 0)
    if code >= 400:
        if ok_conflict and code in (400, 409) and "already" in raw.lower():
            return {"conflict": True}
        sys.exit("%s %s -> HTTP %s: %s" % (method, path, code, raw[:800]))
    try:
        return json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        sys.exit("%s %s -> non-JSON response: %s" % (method, path, raw[:300]))


user = api("GET", "/v2/user")["user"]
print("Authenticated as %s (%s)" % (user.get("username"), user.get("email")))

api("POST", "/v11/projects", {"name": PROJECT, "framework": "astro"}, ok_conflict=True)
print("Project ready: " + PROJECT)

root = os.path.dirname(os.path.abspath(__file__))
files, total = [], 0
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
    for fn in filenames:
        if fn in EXCLUDE_FILES:
            continue
        full = os.path.join(dirpath, fn)
        rel = os.path.relpath(full, root)
        raw = open(full, "rb").read()
        total += len(raw)
        files.append({"file": rel, "data": base64.b64encode(raw).decode(), "encoding": "base64"})

if not files:
    sys.exit("Nothing to deploy.")
if total > MAX_BYTES:
    sys.exit("Source payload %d KB exceeds the %d KB guard." % (total // 1024, MAX_BYTES // 1024))
print("Uploading %d source files (%d KB); Vercel will run the build" % (len(files), total // 1024))

dep = api("POST", "/v13/deployments", {
    "name": PROJECT,
    "project": PROJECT,
    "target": "production",
    "files": files,
    "projectSettings": {
        "framework": "astro",
        "buildCommand": "npm run build",
        "outputDirectory": "dist",
        "installCommand": "npm install",
    },
})
dep_id, dep_url = dep["id"], "https://" + dep["url"]
print("Deployment created: " + dep_url)

state = None
for _ in range(160):
    info = api("GET", "/v13/deployments/" + dep_id)
    state = info["readyState"]
    if state == "READY":
        print("Deployment READY")
        break
    if state in ("ERROR", "CANCELED"):
        print("Deployment %s. Recent build logs:" % state)
        try:
            events = api("GET", "/v3/deployments/%s/events?limit=60" % dep_id)
            for ev in events if isinstance(events, list) else []:
                text = (ev.get("payload") or {}).get("text")
                if text:
                    print("   " + text.rstrip())
        except SystemExit:
            pass
        sys.exit(1)
    time.sleep(5)
else:
    sys.exit("Timed out waiting for READY (last state: %s)" % state)

api("POST", "/v10/projects/%s/domains" % PROJECT, {"name": WWW}, ok_conflict=True)
api("POST", "/v10/projects/%s/domains" % PROJECT,
    {"name": APEX, "redirect": WWW, "redirectStatusCode": 308}, ok_conflict=True)
print("Domains attached: %s (primary), %s (308 redirect)" % (WWW, APEX))

print("\n--- DNS records to set at the registrar ---")
for domain in (APEX, WWW):
    cfg = api("GET", "/v6/domains/%s/config" % domain)
    status = "NEEDS DNS" if cfg.get("misconfigured") else "OK"
    rec = "A     @    76.76.21.21" if domain == APEX else "CNAME www  cname.vercel-dns.com"
    print("%-34s %-10s expected: %s" % (domain, status, rec))

print("\nDeployment URL: %s" % dep_url)
print("Custom domain serves once DNS resolves: https://%s/" % WWW)
