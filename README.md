# Restaurant Idea Generator API

A FastAPI application that uses LangChain and OpenAI to generate creative restaurant concepts with unique names and curated 15-item menus.

## Features

- **AI-Powered Generation**: Unique restaurant names and complete menus via OpenAI
- **Two-Stage Pipeline**: Separate creative (name) and structured (menu) LLM stages
- **Batch Processing**: Generate multiple restaurants in a single request
- **Auto-Repair**: `OutputFixingParser` handles malformed LLM responses
- **Validation**: Multi-layer checks on names, menus, and items
- **Type-Safe**: Full Pydantic v2 model validation on requests and responses

---

## Project Structure

```
restaurant-recommendation/
├── app/
│   ├── main.py               # FastAPI app entry point
│   ├── config.py             # Settings (pydantic-settings, reads app/.env)
│   ├── routes.py             # API endpoints
│   ├── utils.py              # Text, validation, logging, rate-limit helpers
│   ├── models/
│   │   ├── request.py        # Request schemas
│   │   └── response.py       # Response schemas
│   ├── services/
│   │   └── llm_service.py    # LangChain chain builder + RestaurantService
│   └── prompts/
│       └── prompts.py        # PromptTemplate definitions
├── tests/
│   ├── test_llm_service.py   # Unit tests
│   └── test_routes.py        # Integration tests
├── requirements.txt
├── pytest.ini
├── Dockerfile
└── docker-compose.yml
```

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- OpenAI API key

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

Create `app/.env`:

```env
openai_api_key=sk-your-api-key-here
```

Optional overrides (these are the defaults):

```env
MODEL_CREATIVE=gpt-5-nano-2025-08-07
MODEL_STRUCTURED=gpt-5-nano-2025-08-07
TEMP_CREATIVE=0.7
TEMP_STRUCTURED=0.2
max_tokens=2000
debug=False
log_level=INFO
requests_per_minute=10
```

### 4. Run the server

```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

---

## API Reference

### Interactive docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | API info |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/examples` | List example cuisines |
| `POST` | `/api/generate` | Generate one restaurant |
| `POST` | `/api/generate-batch` | Generate multiple restaurants |

### POST /api/generate

```json
// Request
{ "cuisine": "Indian" }

// Response
{
  "success": true,
  "data": {
    "name": "Taj Express",
    "menu": ["Samosa", "Butter Chicken", "Naan", "..."]
  },
  "error": null,
  "timestamp": "2025-05-24T10:30:45.123456"
}
```

### POST /api/generate-batch

```json
// Request
{ "cuisines": ["Indian", "Italian", "Japanese"] }

// Response
{
  "success": true,
  "results": [
    { "cuisine": "Indian", "restaurant": { "name": "...", "menu": [...] } }
  ],
  "failed_cuisines": null,
  "total_requested": 3,
  "total_generated": 3,
  "total_failed": 0,
  "timestamp": "2025-05-24T10:30:45.123456"
}
```

---

## Configuration

All settings are defined in [`app/config.py`](app/config.py) and loaded from `app/.env`.

| Variable | Default | Description |
|----------|---------|-------------|
| `openai_api_key` | *(required)* | OpenAI API key |
| `MODEL_CREATIVE` | `gpt-5-nano-2025-08-07` | Model for name generation |
| `MODEL_STRUCTURED` | `gpt-5-nano-2025-08-07` | Model for menu generation |
| `TEMP_CREATIVE` | `0.7` | Temperature for name generation |
| `TEMP_STRUCTURED` | `0.2` | Temperature for menu generation |
| `max_tokens` | `2000` | Max tokens per LLM call |
| `debug` | `False` | FastAPI debug mode |
| `log_level` | `INFO` | Logging level |
| `requests_per_minute` | `10` | In-process rate limit |

---

## Testing

Tests live in `tests/` and are run from the project root.

```bash
# All tests
pytest

# Specific file
pytest tests/test_llm_service.py -v
pytest tests/test_routes.py -v

# By marker
pytest -m unit
pytest -m integration

# With coverage
pytest --cov=app --cov-report=html
```

---

## How It Works

```
POST /api/generate { "cuisine": "Indian" }
        │
        ▼
[1] Name Chain
    prompt → ChatOpenAI (temp=0.7) → StrOutputParser → clean_text()
    output: "Taj Express"
        │
        ▼
[2] Menu Chain
    prompt (cuisine + name + format_instructions)
    → ChatOpenAI (temp=0.2) → PydanticOutputParser → OutputFixingParser
    output: RestaurantIdea { name, menu[15] }
        │
        ▼
[3] Validation
    validate_restaurant_name / validate_menu_length / validate_menu_items
        │
        ▼
    GenerateRestaurantResponse
```

---

## Error Handling

| Scenario | Status | Response |
|----------|--------|----------|
| Empty / too-short cuisine | `422` | Pydantic validation error |
| LLM generation failed | `200` | `{ "success": false, "error": "..." }` |
| Unexpected server error | `500` | HTTP 500 |

---

## Docker

```bash
# Build and run
docker-compose up --build

# Run container directly
docker run -p 8000:8000 \
  -e openai_api_key=sk-your-key \
  restaurant-generator:latest
```

---

## Troubleshooting

**`openai_api_key` validation error on startup**
- Make sure `app/.env` exists and contains `openai_api_key=sk-...`

**`ModuleNotFoundError` on any `app.*` import**
- Run `uvicorn` from inside the `app/` directory (`cd app` first)

**Menu length validation error**
- The LLM did not return exactly 15 items; `OutputFixingParser` retries automatically — lower `TEMP_STRUCTURED` if it keeps failing

**Port already in use**
- `uvicorn main:app --port 8001`
