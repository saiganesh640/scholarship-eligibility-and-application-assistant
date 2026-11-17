import json, os, sqlite3, hashlib, secrets, time
from datetime import date
from pathlib import Path
from typing import Optional
import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.nlp import SchemeFinder, extract, intent
from app.kb import KnowledgeBase, FORM_GUIDE, L_NSP

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me-dev-secret-change-me")
app, bearer = FastAPI(title="Scholarship Eligibility and Application Assistant"), HTTPBearer()

# ---------- auth ----------
def db():
    c = sqlite3.connect(ROOT / "users.db")
    c.execute("CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, salt TEXT, hash TEXT)")
    return c
def hp(pw, salt): return hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 200_000).hex()
def tok(e): return jwt.encode({"sub": e, "exp": int(time.time()) + 7 * 86400}, SECRET, algorithm="HS256")
def user(c: HTTPAuthorizationCredentials = Depends(bearer)):
    try: return jwt.decode(c.credentials, SECRET, algorithms=["HS256"])["sub"]
    except jwt.PyJWTError: raise HTTPException(401, "Session expired. Please sign in again.")
class Creds(BaseModel): email: str; password: str

@app.post("/api/register")
def register(c: Creds):
    e = c.email.strip().lower()
    if "@" not in e or len(c.password) < 6: raise HTTPException(400, "Enter a valid email and a password of at least 6 characters.")
    salt = secrets.token_hex(16)
    try:
        with db() as con: con.execute("INSERT INTO users VALUES(?,?,?)", (e, salt, hp(c.password, salt)))
    except sqlite3.IntegrityError: raise HTTPException(409, "This email is already registered. Sign in instead.")
    return {"token": tok(e)}

@app.post("/api/login")
def login(c: Creds):
    e = c.email.strip().lower()
    r = db().execute("SELECT salt,hash FROM users WHERE email=?", (e,)).fetchone()
    if not r or not secrets.compare_digest(r[1], hp(c.password, r[0])): raise HTTPException(401, "Email or password is incorrect.")
    return {"token": tok(e)}

# ---------- scholarship engine ----------
SCHEMES = json.loads((ROOT / "data" / "schemes.json").read_text(encoding="utf-8"))
FINDER = SchemeFinder(SCHEMES)
KBASE = KnowledgeBase()
class Profile(BaseModel):
    income: Optional[float] = None; percent: Optional[float] = None; category: Optional[str] = None
    gender: Optional[str] = None; level: Optional[str] = None; state: Optional[str] = None
BASE_DOCS = ["Aadhaar card", "Bank passbook in your name, linked to Aadhaar", "Income certificate", "Previous year marksheet", "Admission or institute ID proof", "Passport-size photo"]
CAT_DOC = {"sc": "Caste certificate", "st": "Caste certificate", "obc": "Caste certificate", "minority": "Minority community declaration", "pwd": "Disability certificate (40% or more)"}
lakh = lambda n: f"₹{n/100000:g} lakh"

def check(p, s):
    fail, unknown = [], []
    def rule(cond_key, val, ok, msg):
        if cond_key not in s: return
        if val is None or val == "": unknown.append(msg[1])
        elif not ok: fail.append(msg[0])
    rule("max_income", p.income, p.income is not None and p.income <= s.get("max_income", 0), (f"Family income is above {lakh(s.get('max_income',0))}", "income"))
    rule("min_percent", p.percent, p.percent is not None and p.percent >= s.get("min_percent", 0), (f"Marks are below {s.get('min_percent')}%", "marks"))
    for key, val, label, unk in [("categories", p.category, "category", "category"), ("genders", p.gender, "gender", "gender"), ("levels", p.level, "course level", "course level"), ("states", p.state, "state", "state")]:
        v = (val or "").lower()
        rule(key, v, v in s.get(key, []), (f"Open only to {label}: {', '.join(s.get(key, []))}", unk))
    days = (date.fromisoformat(s["deadline"]) - date.today()).days if s.get("deadline") else None
    status = "no" if fail else ("maybe" if unknown else "yes")
    return {**{k: s[k] for k in ("id", "name", "ministry", "amount", "description")}, "status": status, "why_not": fail, "missing": sorted(set(unknown)),
            "deadline": s.get("deadline"), "days_left": days, "apply_url": s.get("apply_url", L_NSP["url"]), "info_url": s.get("info_url"), "docs": BASE_DOCS + [CAT_DOC[c] for c in s.get("categories", []) if c in CAT_DOC][:1]}

def rank(p):
    order = {"yes": 0, "maybe": 1, "no": 2}
    return sorted((check(p, s) for s in SCHEMES), key=lambda r: (order[r["status"]], r["days_left"] if r["days_left"] is not None and r["days_left"] >= 0 else 9999))

@app.post("/api/recommend")
def recommend(p: Profile, _: str = Depends(user)):
    r = rank(p)
    return {"results": r, "counts": {k: sum(x["status"] == k for x in r) for k in ("yes", "maybe", "no")}}

@app.get("/api/form-guide")
def form_guide(_: str = Depends(user)): return FORM_GUIDE

@app.get("/api/schemes")
def schemes(_: str = Depends(user)): return [check(Profile(), s) for s in SCHEMES]

# ---------- chat ----------
class ChatIn(BaseModel): message: str; profile: Profile = Profile()
def dl(r):
    if r["days_left"] is None: return "check the NSP portal for the date"
    return "closed" if r["days_left"] < 0 else f'{r["deadline"]} ({r["days_left"]} days left)'
def names(rs, n=6): return "\n".join(f"• {r['name']}: {r['amount']}" for r in rs[:n])

@app.post("/api/chat")
def chat(b: ChatIn, _: str = Depends(user)):
    updates = extract(b.message)
    it, _c = intent(b.message)
    s = FINDER.find(b.message)
    if len(updates) >= 3 and it in ("fallback", "eligibility", "recommend"): s, it = None, "recommend"  # user described themselves
    elif s and len(updates) < 2: updates = {}  # a scheme name like "post matric sc" is not a profile
    p = Profile(**{**b.profile.model_dump(), **updates})
    res = rank(p); yes = [r for r in res if r["status"] == "yes"]; maybe = [r for r in res if r["status"] == "maybe"]
    kb, kscore = KBASE.find(b.message)
    strict = it in ("fallback", "apply", "documents", "eligibility", "help") and kscore >= 0.3
    use_kb = kb and not (s and it in ("documents", "deadline", "amount", "eligibility", "recommend")) and not (it in ("recommend", "list", "deadline") and kscore < 0.95) and (kscore >= 0.45 or strict)
    known = sum(v is not None for v in p.model_dump().values())
    r = next((x for x in res if s and x["id"] == s["id"]), None)
    links, sugg = [], None
    if use_kb: reply, links = kb["a"], kb.get("links", [])
    elif it == "greet": reply = "Hello! Tell me about yourself, for example: \"I am an OBC girl in B.Tech, family income 2 lakh, 78% marks, from Odisha\". I will find the scholarships that fit."
    elif it == "thanks": reply = "You're welcome. Ask me about deadlines, documents or how to apply for any scheme."
    elif it == "help" and not r: reply = "I can match you to NSP scholarships, explain why you do or don't qualify, and give deadlines, documents, amounts and application steps. Share your income, marks, category, course level and state to start."
    elif it == "list" and not r: reply = f"There are {len(SCHEMES)} schemes in my database:\n" + "\n".join(f"• {x['name']}" for x in SCHEMES)
    elif it == "deadline" and not r:
        dated = [x for x in res if x["days_left"] is not None and x["days_left"] >= 0 and x["status"] != "no"] or [x for x in res if x["days_left"] is not None and x["days_left"] >= 0]
        reply = "Upcoming deadlines:\n" + "\n".join(f"• {x['name']}: {dl(x)}" for x in dated[:6]) if dated else "None of the schemes I have list a confirmed open date. Check scholarships.gov.in for current windows."
        reply += "\n\nMost NSP schemes are reported to close on 31 October 2026 (third-party listings). Confirm on the portal and apply by September."
    elif it == "apply": reply = "How to apply on NSP:\n1. Register on scholarships.gov.in (One Time Registration with Aadhaar).\n2. Log in and choose your scheme.\n3. Fill the application and upload documents.\n4. Submit, then note your application ID.\n5. Your institute and state officials verify it. Track the status on the portal."
    elif r and it == "documents": reply = f"Documents for {r['name']}:\n" + "\n".join(f"• {d}" for d in r["docs"])
    elif r and it == "deadline": reply = f"{r['name']}: {dl(r)}."
    elif r and it == "amount": reply = f"{r['name']} gives {r['amount']}."
    elif r and it in ("eligibility", "recommend", "fallback"):
        if r["status"] == "yes": reply = f"Yes, you meet every rule I have for {r['name']}. Benefit: {r['amount']}. Deadline: {dl(r)}."
        elif r["status"] == "no": reply = f"You don't qualify for {r['name']} because:\n" + "\n".join(f"• {w}" for w in r["why_not"])
        else: reply = f"{r['name']}: {r['description']}\nI need your {', '.join(r['missing'])} to confirm eligibility."
    elif r: reply = f"{r['name']} ({r['ministry']}): {r['description']}\nBenefit: {r['amount']}. Deadline: {dl(r)}."
    elif it in ("recommend", "eligibility") or updates:
        if yes: reply = f"You qualify for {len(yes)} scheme(s):\n{names(yes)}" + (f"\n\n{len(maybe)} more could fit if you add missing details." if maybe else "")
        elif maybe: reply = "No confirmed match yet, but these could fit once I know more:\n" + names(maybe, 4)
        else: reply = "No scheme matches this profile right now. Check the details on the left, or ask about a specific scheme."
    else: reply, sugg = "I didn't catch that. Tell me your course level, category, income, marks and state, or ask about a scheme, OTR, documents, or filling the NSP form.", ["What is OTR?", "How do I fill the form?", "What documents do I need?"]
    if r and not use_kb:
        links = [{"label": "Apply on NSP" if r["apply_url"] == L_NSP["url"] else "Apply here", "url": r["apply_url"]}] + ([{"label": "Ministry website", "url": r["info_url"]}] if r["info_url"] else [])
        short = r["name"].split(" (")[0][:38]
        sugg = [f"Documents for {short}", "How do I fill the form?", "Which deadlines are closing soon?"]
    elif it in ("recommend", "eligibility") and yes: links, sugg = [L_NSP], ["How do I fill the form?", "What is OTR?", "Which deadlines are closing soon?"]
    ask = [f for f, v in [("family income", p.income), ("marks", p.percent), ("category", p.category), ("course level", p.level)] if v is None]
    if it in ("recommend", "eligibility", "fallback") and ask and not r and not use_kb: reply += f"\n\nTo sharpen this, tell me your {', '.join(ask[:2])}."
    return {"reply": reply, "profile_updates": updates, "highlight": r["id"] if r else None, "links": links, "suggest": sugg}

app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
@app.get("/")
def index(): return FileResponse(ROOT / "static" / "index.html")
