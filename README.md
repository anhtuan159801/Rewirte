# DOCX Rewrite System

MVP he thong ho tro chinh sua tai lieu `DOCX` dua tren `PDF` bao cao tuong dong.

## Tinh nang chinh

- Upload `DOCX` va `PDF`
- Parse noi dung tai lieu va bao cao
- Alignment doan nghi ngo tu report vao paragraph trong DOCX
- Rewrite theo thu tu provider `Groq -> OpenRouter -> Gemini`
- Validate output, gan co `citation_needed`
- Tao `revised.docx` va `change_report.json`
- UI toi thieu cho upload, theo doi job, review

## Chay backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

## Chay frontend

```bash
cd frontend
npm install
npm run dev
```

Dat `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000` neu can.

## Bien moi truong

```env
APP_ENV=development
STORAGE_PATH=./storage

GROQ_API_KEY=
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.3-70b-versatile

OPENROUTER_API_KEY=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=google/gemini-2.5-pro

GEMINI_API_KEY=
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
GEMINI_MODEL=gemini-2.5-pro

LLM_TIMEOUT_SECONDS=30
MAX_PROVIDER_RETRIES=1
LOG_LEVEL=INFO
```

Neu chua co API key, provider se chay o che do mock de demo luong xu ly end-to-end.

## Test

```bash
pytest
```
