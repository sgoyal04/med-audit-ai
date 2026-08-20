# MedAudit AI — Clinical Document Intelligence & Chronology Pipeline

An end-to-end medical records processing platform that extracts, structures, and validates chronological clinical timelines from multi-page medical PDFs.

---

## 📌 Problem Statement

Reviewing medical charts for insurance audits, legal reviews, and clinical analysis is typically a manual, time-consuming process. Medical records are often disorganized, multi-page PDFs with fragmented encounter notes, doctor summaries, prescriptions, and lab tests scattered across non-sequential pages.

**MedAudit AI solves this by:**

- Automating the extraction and parsing of raw medical PDFs into structured data.
- Sorting all patient encounters, lab tests, and prescriptions into a chronological timeline.
- Grounding every extracted event with the exact source page number and verbatim quote for zero-hallucination verification.
- Providing a multi-case dashboard where auditors can manage, review, and analyze multiple patient records securely.

---

## 🛠️ Tech Stack

- **Data Processing & Backend:** Python, PyMuPDF, FastAPI, Pydantic, Uvicorn
- **Database & Storage:** PostgreSQL (`JSONB`), SQLAlchemy ORM
- **LLM & Extraction Engine:** Google Gemini API (Structured Outputs & Schema Validation)
- **Frontend & UI:** Next.js (App Router), TypeScript, Tailwind CSS, Lucide Icons
- **Authentication:** OAuth 2.0 (Google & GitHub Social Logins) + JWT (JSON Web Tokens)

---

## 🚀 Key Highlights (Data & Engineering Focus)

- **End-to-End ETL Pipeline:** Ingests raw PDF bytes, extracts per-page document text, and converts unstructured records into clean, validated JSON.
- **Strict Schema Validation:** Enforces Pydantic data models to eliminate LLM hallucinations and guarantee predictable, standardized formats (ISO dates, encounter types, medication lists).
- **Semi-Structured Relational Storage:** Utilizes PostgreSQL `JSONB` to store complex nested clinical timelines while supporting fast queries across patient cases.
- **1-Click Audit Traceability:** Integrates deep-linked source page citations, enabling users to click any timeline event and immediately verify the quote in the embedded PDF viewer.
- **Multi-Tenant User Management:** Scopes clinical cases to authenticated user accounts via OAuth 2.0 and JWTs, allowing adjusters to manage multiple open cases across sessions.

## ⚙️ How to Run

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** & npm
- **Google Gemini API Key** ([Google AI Studio](https://aistudio.google.com/))

---

### 1. Clone the Repository

```bash
git clone https://github.com/sgoyal04/med-audit-ai.git
cd medaudit-ai
```

### 2. Backend Setup (FastAPI)

1. Open a terminal and navigate to the backend directory:

```bash
cd backend

```

2. Create and activate a Python virtual environment:

```bash
# macOS / Linux:
python3 -m venv venv
source venv/bin/activate

# Windows:
python -m venv venv
venv\Scripts\activate

```

3. Install the dependencies:

```bash
pip install -r requirements.txt

```

4. Create a `.env` file inside the `backend/` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here

```

5. Start the FastAPI server:

```bash
uvicorn main:app --reload --port 8000

```

_The API will be live at `http://localhost:8000` (Interactive Swagger docs at `http://localhost:8000/docs`)._

---

### 3. Frontend Setup (Next.js)

1. Open a second terminal window and navigate to the frontend directory:

```bash
cd frontend

```

2. Install the frontend dependencies:

```bash
npm install

```

3. Create a `.env.local` file inside the `frontend/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000

```

4. Start the Next.js development server:

```bash
npm run dev

```

5. Open your browser and navigate to **`http://localhost:3000`** to upload medical charts and view the interactive timeline.
