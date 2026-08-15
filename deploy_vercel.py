#!/usr/bin/env python3
"""One-shot Vercel production deploy for singaporebusinessbroker.com.

Uploads every static file in this directory to the Vercel project
`singaporebusinessbroker` (created if missing), promotes the deployment to
production, attaches the custom domains, and prints the DNS records to set.

Requires a Vercel personal access token in env var `VERCEL_TOKEN` (or `vercel`).
Usage: python3 deploy_vercel.py
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.vercel.com"
PROJECT = "singaporebusinessbroker"
APEX = "singaporebusinessbroker.com"
WWW = "www." + APEX

# Directories skipped wholesale, and individual files never deployed.
EXCLUDE_DIRS = {".git", ".github", "node_modules", "__pycache__", ".vercel"}
EXCLUDE_FILES = {"build.py", "deploy_vercel.py", "README.md", ".gitignore", ".DS_Store"}

TOKEN = os.environ.get("VERCEL_TOKEN") or os.environ.get("vercel")
if not TOKEN:
    sys.exit("No Vercel token: set VERCEL_TOKEN (or `vercel`) in the environment.")


def api(method, path, body=None, ok_conflict=False):
    req = urllib.request.Request(API + path, method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    data = None
    if body is not None:
        req.add_header("Content-Type", "application/json")
        data = json.dumps(body).encode()
    try:
        with urllib.request.urlopen(req, data, timeout=180) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        if ok_conflict and e.code in (400, 409) and "already" in detail.lower():
            return {"conflict": True}
        sys.exit("%s %s -> HTTP %s: %s" % (method, path, e.code, detail[:600]))


user = api("GET", "/v2/user")["user"]
print("Authenticated as %s (%s)" % (user.get("username"), user.get("email")))

api("POST", "/v11/projects", {"name": PROJECT, "framework": None}, ok_conflict=True)
print("Project ready: " + PROJECT)

root = os.path.dirname(os.path.abspath(__file__))
files, total = [], 0
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
    for fn in filenames:
        rel = os.path.relpath(os.path.join(dirpath, fn), root)
        if fn in EXCLUDE_FILES:
            continue
        raw = open(os.path.join(dirpath, fn), "rb").read()
        total += len(raw)
        files.append({"file": rel, "data": base64.b64encode(raw).decode(),
                      "encoding": "base64"})
if not files:
    sys.exit("Nothing to deploy — did you run build.py?")
print("Uploading %d files (%d KB)" % (len(files), total // 1024))

dep = api("POST", "/v13/deployments", {
    "name": PROJECT,
    "project": PROJECT,
    "target": "production",
    "files": files,
    "projectSettings": {"framework": None},
})
dep_id, dep_url = dep["id"], "https://" + dep["url"]
print("Deployment created: " + dep_url)

for _ in range(90):
    state = api("GET", "/v13/deployments/" + dep_id)["readyState"]
    if state == "READY":
        print("Deployment READY")
        break
    if state in ("ERROR", "CANCELED"):
        sys.exit("Deployment failed: " + state)
    time.sleep(5)
else:
    sys.exit("Timed out waiting for the deployment to become READY")

api("POST", "/v10/projects/%s/domains" % PROJECT, {"name": WWW}, ok_conflict=True)
api("POST", "/v10/projects/%s/domains" % PROJECT,
    {"name": APEX, "redirect": WWW, "redirectStatusCode": 308}, ok_conflict=True)
print("Domains attached: %s (primary), %s (308 redirect)" % (WWW, APEX))

print("\n--- DNS records to set at the registrar ---")
for domain in (APEX, WWW):
    cfg = api("GET", "/v6/domains/%s/config" % domain)
    status = "NEEDS DNS" if cfg.get("misconfigured") else "OK"
    rec = ("A     @    76.76.21.21" if domain == APEX
           else "CNAME www  cname.vercel-dns.com")
    print("%-32s %-10s expected: %s" % (domain, status, rec))

print("\nLive now at: %s" % dep_url)
print("Custom domain serves once DNS resolves: https://%s/" % WWW)
