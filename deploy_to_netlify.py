#!/usr/bin/env python3
"""
CSZone Netlify Batch Deploy
Deploys all 47 OCR J277 lesson pages in ONE Netlify deploy = 15 credits total.

Run from this folder:
  cd C:/Users/Mojib/OneDrive/Desktop/CSZone_Deploy
  python deploy_to_netlify.py
"""

import os
import sys
import hashlib
import json
import glob
import urllib.request
import urllib.error
import urllib.parse

# ── Config ───────────────────────────────────────────────────────────────────
NETLIFY_TOKEN = "nfp_Fc7Te8DPW84BuHXwSd3BKJYFBBCzaS6r2992"
SITE_ID       = "bde6dde3-e809-4638-b9ff-28123a6e5797"
OUTPUTS_DIR   = os.path.dirname(os.path.abspath(__file__))

# Existing live files — carry their SHAs forward so Netlify doesn't delete them
CARRY_FORWARD = {
    "/index.html":           "f2a515d0abe0fe7f03746fb8c80c5540619d985e",
    "/dashboard/index.html": "1029ab31e9c15d604397f83f04887866da7c42c7",
    "/admin/index.html":     "e7b88c70bd0fbaf9fe06f8c60bcf8780788a4b94",
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

def filename_to_path(filename):
    # CSZone_Lesson_1_2_4a.html -> /ocr-j277/1-2-4a/index.html
    slug = filename.replace("CSZone_Lesson_", "").replace(".html", "").replace("_", "-")
    return "/ocr-j277/" + slug + "/index.html"

def api(method, endpoint, body=None, raw_bytes=False):
    url = "https://api.netlify.com/api/v1" + endpoint + "?access_token=" + NETLIFY_TOKEN
    if raw_bytes:
        data, ctype = body, "application/octet-stream"
    elif body is not None:
        data, ctype = json.dumps(body).encode(), "application/json"
    else:
        data, ctype = None, "application/json"
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", ctype)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print("  HTTP " + str(e.code) + ": " + e.read().decode()[:300])
        raise

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    lesson_files = sorted(glob.glob(os.path.join(OUTPUTS_DIR, "CSZone_Lesson_*.html")))
    print("Folder : " + OUTPUTS_DIR)
    print("Found  : " + str(len(lesson_files)) + " HTML lesson files\n")

    if not lesson_files:
        print("ERROR: No CSZone_Lesson_*.html files found in this folder.")
        print("Make sure all HTML files are in the same folder as this script.")
        sys.exit(1)

    files = dict(CARRY_FORWARD)
    sha_to_local = {}

    for local in lesson_files:
        fname         = os.path.basename(local)
        npath         = filename_to_path(fname)
        fsha          = sha1(local)
        files[npath]  = fsha
        sha_to_local[fsha] = local
        print("  " + npath)

    print("\nTotal files in deploy: " + str(len(files)) + " (" + str(len(lesson_files)) + " lessons + " + str(len(CARRY_FORWARD)) + " existing)\n")

    print("Creating Netlify deploy (15 credits)...")
    deploy    = api("POST", "/sites/" + SITE_ID + "/deploys", {"files": files})
    deploy_id = deploy["id"]
    required  = deploy.get("required", [])
    print("  Deploy ID : " + deploy_id)
    print("  To upload : " + str(len(required)) + " new file(s)\n")

    if required:
        print("Uploading...")
        for i, fsha in enumerate(required, 1):
            local = sha_to_local.get(fsha)
            if not local:
                print("  [" + str(i) + "/" + str(len(required)) + "] SHA " + fsha[:10] + " already cached")
                continue
            npath = filename_to_path(os.path.basename(local))
            print("  [" + str(i) + "/" + str(len(required)) + "] " + npath + "...", end=" ", flush=True)
            with open(local, "rb") as f:
                content = f.read()
            api("PUT", "/deploys/" + deploy_id + "/files" + urllib.parse.quote(npath), content, raw_bytes=True)
            print("OK (" + str(len(content)) + " bytes)")
    else:
        print("All files already cached — no uploads needed.")

    print("\n" + "=" * 55)
    print("DEPLOY COMPLETE")
    print("  Live  : https://cszone.co.uk")
    print("  Admin : https://app.netlify.com/projects/cszone/deploys/" + deploy_id)
    print("  Cost  : 15 credits")
    print("=" * 55)

if __name__ == "__main__":
    main()
