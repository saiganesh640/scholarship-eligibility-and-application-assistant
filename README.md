# Scholarship Eligibility Application Assistant 

No external LLM or API. Everything runs on your machine.

**How it works (your own AI):** `app/nlp.py` extracts your details from plain text, classifies what you are asking (TF-IDF + cosine similarity), finds the scheme you mean, and the rule engine in `app/main.py` decides eligibility.

**What it does by itself:** reads your income, marks, category, level and state from chat and fills your profile; re-ranks all schemes live; sorts by deadline; tells you what detail is missing.

## Run
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` (set a long JWT_SECRET)
3. `python -m uvicorn app.main:app --reload`
4. Open http://127.0.0.1:8000

## Add your full NSP list
`data/schemes.json` has 19 central scheme records. Income limits and dates change every year, so verify each on scholarships.gov.in. To load your own listings: put them in a CSV (columns in `tools/import_listings.py`) and run `python tools/import_listings.py my_listings.csv`.
