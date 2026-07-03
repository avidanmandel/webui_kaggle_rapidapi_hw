# Open WebUI + Kaggle Knowledge Base + RapidAPI Tool

Homework project for Open WebUI: combine a **Knowledge Base** (Kaggle CSV) with a **Tool** (live country data via a local Flask server and RapidAPI).

## Project goal

Build an assistant in Open WebUI that answers two kinds of questions:

| Question type | Example | Source |
|---------------|---------|--------|
| Dataset / rankings | Which university was ranked #1 in 2012? | **Knowledge Base** (`cwurData.csv`) |
| Live / external | What is the capital of Japan? | **Country Info Tool** → `tools_server.py` → RapidAPI |

This demonstrates **static RAG** (uploaded CSV) vs **dynamic tool use** (live API at query time).

## Architecture

```
Open WebUI
  │
  ├─ Knowledge Base (cwurData.csv)
  │    → RAG retrieval for university rankings / scores / dataset questions
  │    → No external API call
  │
  └─ Country Info Tool (openwebui_tool.py)
       → get_country_info("Japan")
       → http://host.docker.internal:5005/country-info?country=Japan
            │
            └─ tools_server.py (Flask :5005)
                 → RapidAPI GET .../all  (RAPIDAPI_MODE=all_filter)
                 → Filter country list locally by name
                 → Fallback public list if RapidAPI /all is unavailable
```

### How the Knowledge Base uses `cwurData.csv`

1. Upload `cwurData.csv` in Open WebUI → **Workspace → Knowledge**.
2. Open WebUI indexes the CSV for retrieval (RAG).
3. Attach the Knowledge collection to a chat.
4. Rankings questions retrieve relevant rows from the CSV — the model answers from dataset content, not from RapidAPI.

### How the Country Info Tool calls `tools_server.py`

1. Paste `openwebui_tool.py` into **Workspace → Tools** and enable it in chat.
2. When the user asks for live country facts, the model calls `get_country_info(country)`.
3. The tool sends `GET http://host.docker.internal:5005/country-info?country=...` to your local Flask server.
4. The server returns JSON; the model uses it to answer (e.g. capital of Japan → Tokyo).

### How `tools_server.py` uses RapidAPI and fallback

1. Reads credentials from local `.env` (never committed).
2. **`RAPIDAPI_MODE=all_filter`** — calls `https://restcountries-v1.p.rapidapi.com/all` with RapidAPI headers.
3. Receives a list of countries and filters locally by name (case-insensitive).
4. If RapidAPI `/all` is unavailable, uses a public fallback country list so homework testing still works.
5. Returns clean JSON from `/country-info`; `/health` confirms the server is up.

## Project structure

```
webui_kaggle_rapidapi_hw/
├── tools_server.py
├── openwebui_tool.py
├── test_local_server.py
├── requirements.txt
├── .env.example          # Template only — no real keys
├── .gitignore
├── README.md
├── cwurData.csv
├── data/.gitkeep
└── screenshots/          # Submission PNG files (see list below)
```

## Run locally

### 1. Install

```powershell
cd webui_kaggle_rapidapi_hw
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure (local only)

```powershell
copy .env.example .env
```

Edit `.env` and add your RapidAPI key. Values in `.env.example`:

- `RAPIDAPI_HOST=restcountries-v1.p.rapidapi.com`
- `RAPIDAPI_URL=https://restcountries-v1.p.rapidapi.com/all`
- `RAPIDAPI_MODE=all_filter`

> **Security:** `.env` is in `.gitignore` and must **never** be committed.

### 3. Start server

```powershell
python tools_server.py
```

Keep running on **`0.0.0.0:5005`**.

### 4. Test `/health`

```powershell
curl.exe http://localhost:5005/health
```

Expected: `{"status":"ok","service":"tools_server"}`

### 5. Test `/country-info`

```powershell
curl.exe "http://localhost:5005/country-info?country=Japan"
```

Expected: HTTP 200, JSON with `"country":"Japan"` and country data.

Or: `python test_local_server.py`

## Open WebUI setup

### Add Knowledge Base

1. **Workspace → Knowledge** → upload `cwurData.csv`
2. Wait for indexing
3. New chat → attach Knowledge collection
4. Ask rankings questions (e.g. top university in 2012)

### Add Country Info Tool

1. **Workspace → Tools** → Create New Tool
2. Paste entire `openwebui_tool.py` → Save
3. Chat → **+** menu → enable Country Info Tool
4. Use a model with function calling
5. Keep `tools_server.py` running
6. Ask: *What is the capital of Japan?*

## Screenshots for submission

Save in `screenshots/` with these exact names:

| File | Content |
|------|---------|
| `01_knowledge_base_uploaded.png` | Knowledge page, `cwurData.csv` indexed |
| `02_country_info_tool_created.png` | Workspace → Tools, Country Info Tool |
| `03_knowledge_base_chat_csv_source.png` | Chat with retrieved source / `cwurData.csv` |
| `04_country_tool_chat_japan_tokyo.png` | Tool call + Japan capital = Tokyo |
| `05_terminal_health_ok.png` | `curl.exe .../health` → status ok |
| `06_terminal_country_info_japan_ok.png` | `curl.exe .../country-info?country=Japan` → 200 |
| `07_tools_server_running.png` | *(optional)* Server on port 5005 |

See `screenshots/SCREENSHOTS_TODO.md` if any files are still missing.

## Verified completion

- `tools_server.py` on port 5005
- `/health` OK
- `/country-info?country=Japan` OK
- Knowledge Base retrieves from `cwurData.csv`
- Country Info Tool returns Japan capital = Tokyo

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Tool cannot connect | Run `tools_server.py`; use `host.docker.internal:5005` from Docker |
| RapidAPI errors | Check `.env` key and REST Countries v1 subscription |
| Country 404 | Use country name (`Japan`), not numbers |
| Rankings wrong | Attach Knowledge Base; confirm CSV indexed |

## License

Student homework project — educational use only.
