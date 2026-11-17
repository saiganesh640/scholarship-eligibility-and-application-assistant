"""Load your own scholarship listings into data/schemes.json.
Usage: python tools/import_listings.py my_listings.csv
CSV columns: name,ministry,levels,categories,genders,states,max_income,min_percent,amount,deadline,description,apply_url,info_url
Use | between multiple values (e.g. levels = undergraduate|postgraduate). deadline as YYYY-MM-DD."""
import csv, json, re, sys
from pathlib import Path
path = Path(__file__).resolve().parent.parent / "data" / "schemes.json"
data = json.loads(path.read_text(encoding="utf-8"))
by_name = {d["name"].lower(): d for d in data}
for row in csv.DictReader(open(sys.argv[1], encoding="utf-8-sig")):
    s = {"id": re.sub(r"[^a-z0-9]+", "-", row["name"].lower()).strip("-")[:40], "name": row["name"].strip(), "ministry": row.get("ministry", ""),
         "amount": row.get("amount", ""), "description": row.get("description", ""), "aliases": row["name"].lower()}
    for k in ("levels", "categories", "genders", "states"):
        if row.get(k): s[k] = [x.strip().lower() for x in row[k].split("|") if x.strip()]
    for k, cast in (("max_income", float), ("min_percent", float)):
        if row.get(k): s[k] = cast(row[k])
    for k in ("apply_url", "info_url"):
        if row.get(k): s[k] = row[k]
    if row.get("deadline"): s["deadline"] = row["deadline"]
    by_name[s["name"].lower()] = s
path.write_text(json.dumps(list(by_name.values()), indent=1, ensure_ascii=False), encoding="utf-8")
print(f"{len(by_name)} schemes now in data/schemes.json")
