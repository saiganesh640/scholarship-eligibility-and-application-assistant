# Scholarship Eligibility and Application Assistant

A web-based academic project that helps students explore scholarship opportunities, assess eligibility, receive recommendations, and get application guidance through a conversational interface.

> **Important:** Scholarship rules, income limits, deadlines, and application links can change. The bundled dataset is for demonstration and must be verified against the official National Scholarship Portal before applying.

## Features

- Student registration and login with JWT-based authentication.
- Student profile input for academic and personal eligibility details.
- Scholarship listing from a local JSON dataset.
- Rule-based eligibility checks against scholarship criteria.
- Scholarship recommendations ranked using eligibility and relevance logic.
- Chat-based scholarship assistance using TF-IDF and cosine similarity.
- Application form and document guidance.
- CSV utility for importing scholarship listings.

## Technology Stack

- **Backend:** Python, FastAPI, Uvicorn
- **NLP:** scikit-learn, TF-IDF, cosine similarity
- **Authentication:** JWT and PBKDF2 password hashing
- **Data:** JSON scholarship dataset and SQLite local user records
- **Frontend:** HTML, CSS, JavaScript

## Project Structure

```text
app/
  main.py
  nlp.py
  kb.py
data/
  schemes.json
static/
  index.html
tools/
  import_listings.py
.env.example
.gitignore
requirements.txt
README.md
```

## Requirements

- Python 3.10+
- pip

## Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/saiganesh640/scholarship-eligibility-and-application-assistant.git
   cd scholarship-eligibility-and-application-assistant
   ```

2. Create and activate a virtual environment:

   **Windows PowerShell**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   **macOS / Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and set a unique, long `JWT_SECRET`. Never commit `.env`.

5. Start the application:

   ```bash
   python -m uvicorn app.main:app --reload
   ```

6. Open http://127.0.0.1:8000. API documentation is available at http://127.0.0.1:8000/docs.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/register` | Register a student |
| POST | `/api/login` | Authenticate and obtain a token |
| POST | `/api/recommend` | Assess eligibility and return recommendations |
| GET | `/api/form-guide` | Retrieve application/document guidance |
| GET | `/api/schemes` | Retrieve scholarship schemes |
| POST | `/api/chat` | Ask the scholarship assistant a question |

## Scholarship Dataset

The repository includes scholarship scheme records in `data/schemes.json`. They are demonstration data. Verify current eligibility rules, award values, deadlines and official URLs with the relevant official scholarship authorities before using them.

To import additional records, prepare a CSV with the columns expected by `tools/import_listings.py`, then run:

```bash
python tools/import_listings.py path/to/listings.csv
```

## Security and Data Handling

- `.env` is excluded by `.gitignore`; only `.env.example` is included.
- Local SQLite database files and virtual environments are excluded.
- Do not commit real student records, credentials, tokens, API keys or private information.

## Project Team

- **Sai Ganesh:** Backend development, APIs, database, eligibility and recommendation logic.
- **Sindhuja:** Frontend development and user interface.
- **Harshabardhan:** Frontend/backend integration, testing and debugging.

## Disclaimer

This is an academic project, not an official government service. It does not guarantee scholarship eligibility or award approval. Students must verify all scheme details and submit applications through official portals.
