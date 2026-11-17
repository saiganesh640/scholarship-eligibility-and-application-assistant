"""Scholar AI language engine: written from scratch, no external LLM or API.
Pipeline: entity extraction (regex) -> intent classification (TF-IDF + cosine) -> scheme detection -> reply templates."""
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

INTENTS = {
 "greet": ["hi", "hello", "hey there", "good morning", "namaste"],
 "thanks": ["thanks", "thank you", "great thanks", "ok got it"],
 "help": ["what can you do", "help me", "how do i use this"],
 "list": ["list all scholarships", "show all schemes", "what scholarships are available", "all scholarships on nsp"],
 "recommend": ["which scholarships can i apply for", "am i eligible for any scholarship", "suggest scholarships for me", "find scholarships that match my profile", "what do i qualify for"],
 "deadline": ["last date to apply", "deadline", "which scholarships close soon", "when does it close", "due date"],
 "documents": ["documents required", "what documents do i need", "which certificates are needed", "papers needed to apply"],
 "apply": ["how to apply", "application process", "how do i register on nsp", "steps to apply online"],
 "amount": ["how much money will i get", "scholarship amount", "what is the benefit", "how much is the award"],
 "eligibility": ["eligibility criteria", "who can apply", "am i eligible for this scheme", "income limit for this scholarship"],
}
_lab, _txt = [], []
for k, v in INTENTS.items():
    for t in v: _lab.append(k); _txt.append(t)
_iv = TfidfVectorizer(ngram_range=(1, 2)); _im = _iv.fit_transform(_txt)

STATES = ["andhra pradesh","arunachal pradesh","assam","bihar","chhattisgarh","goa","gujarat","haryana","himachal pradesh","jharkhand","karnataka","kerala","madhya pradesh","maharashtra","manipur","meghalaya","mizoram","nagaland","odisha","punjab","rajasthan","sikkim","tamil nadu","telangana","tripura","uttar pradesh","uttarakhand","west bengal","delhi","jammu and kashmir","ladakh"]

def extract(text):
    t, out = " " + text.lower() + " ", {}
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs)\b", t)
    if m: out["income"] = float(m.group(1)) * 100000
    else:
        m = re.search(r"income[^\d]{0,20}(\d{5,8})", t) or re.search(r"[₹]\s*(\d{5,8})", t)
        if m: out["income"] = float(m.group(1))
    m = re.search(r"(\d{2,3}(?:\.\d+)?)\s*(?:%|percent|per cent|percentage)", t)
    if m and float(m.group(1)) <= 100: out["percent"] = float(m.group(1))
    for cat, pat in [("minority", r"minorit|muslim|christian|sikh|buddhist|jain|parsi"), ("pwd", r"disab|divyang|\bpwd\b"),
                     ("obc", r"\bobc\b|\bebc\b"), ("sc", r"\bsc\b|scheduled caste"), ("st", r"\bst\b|scheduled tribe|tribal"), ("general", r"\bgeneral\b|\bews\b")]:
        if re.search(pat, t): out["category"] = cat; break
    if re.search(r"\b(female|girl|woman|women|she)\b", t): out["gender"] = "female"
    elif re.search(r"\b(male|boy|man|men)\b", t): out["gender"] = "male"
    for lvl, pat in [("phd", r"ph\.?d|doctoral|research scholar"), ("postgraduate", r"postgrad|post-grad|\bpg\b|m\.?tech|\bmba\b|\bmsc\b|master"),
                     ("undergraduate", r"undergrad|\bug\b|b\.?tech|\bbe\b|bachelor|degree|\bbsc\b|\bbca\b|engineering"),
                     ("diploma", r"diploma|polytechnic|\biti\b"), ("school", r"class\s*\d+|school|\b(9|10|11|12)(th)?\b|intermediate")]:
        if re.search(pat, t): out["level"] = lvl; break
    for s in STATES:
        if s in t: out["state"] = s; break
    return out

def intent(text):
    sims = cosine_similarity(_iv.transform([text.lower()]), _im)[0]
    i = sims.argmax()
    return (_lab[i], float(sims[i])) if sims[i] >= 0.2 else ("fallback", 0.0)

class SchemeFinder:
    def __init__(self, schemes):
        self.s = schemes
        self.v = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.m = self.v.fit_transform([f'{x["name"]} {x.get("aliases","")}' for x in schemes])
    def find(self, text):
        sims = cosine_similarity(self.v.transform([text.lower()]), self.m)[0]
        i = sims.argmax()
        return self.s[i] if sims[i] >= 0.3 else None
