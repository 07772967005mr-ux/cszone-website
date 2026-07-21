"""
Fix: replace wrong localStorage key 'sb-access-token'
with the correct Supabase v2 key 'sb-jxrqlnlsslftcqeyyzbx-auth-token'
across all 35 paid lesson HTML files.
"""
import os, glob

DEPLOY_DIR = os.path.dirname(os.path.abspath(__file__))
OLD = "localStorage.getItem('sb-access-token')"
NEW = "(function(){try{var d=JSON.parse(localStorage.getItem('sb-jxrqlnlsslftcqeyyzbx-auth-token')||'{}');return d.access_token||'';}catch(e){return '';}}())"

files = glob.glob(os.path.join(DEPLOY_DIR, "CSZone_Lesson_*.html"))
fixed = 0
for f in sorted(files):
    content = open(f, encoding='utf-8').read()
    if OLD in content:
        new_content = content.replace(OLD, NEW)
        open(f, 'w', encoding='utf-8').write(new_content)
        count = content.count(OLD)
        print("Fixed " + str(count) + "x in " + os.path.basename(f))
        fixed += 1

print("\nDone — " + str(fixed) + " files patched.")
print("Now run: python deploy_to_netlify.py")
