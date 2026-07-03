# Screenshots TODO

Three screenshots are **done**. Four are still **missing**.

Before saving any screenshot, verify it does **not** show:
- Your `.env` file contents
- Your RapidAPI API key
- Terminal output containing secrets

## Completed

- [x] `02_country_info_tool_created.png`
- [x] `03_knowledge_base_chat_csv_source.png`
- [x] `04_country_tool_chat_japan_tokyo.png`

## Still missing

### 01_knowledge_base_uploaded.png
**Capture:** Open WebUI → Workspace → Knowledge  
**Show:** `cwurData.csv` uploaded and indexed (indexing complete).

### 05_terminal_health_ok.png
**Capture:** Terminal  
**Command:** `curl.exe http://localhost:5005/health`  
**Show:** Response with `"status":"ok"`.

### 06_terminal_country_info_japan_ok.png
**Capture:** Terminal  
**Command:** `curl.exe "http://localhost:5005/country-info?country=Japan"`  
**Show:** HTTP 200 and JSON with `"country":"Japan"`.

### 07_tools_server_running.png *(optional)*
**Capture:** Terminal running `python tools_server.py`  
**Show:** Flask server listening on `0.0.0.0:5005`.

## After capturing

```powershell
cd "C:\Users\avida\amdocs\lesson 17\webui_kaggle_rapidapi_hw"
git add screenshots/01_knowledge_base_uploaded.png screenshots/05_terminal_health_ok.png screenshots/06_terminal_country_info_japan_ok.png
git commit -m "Add remaining homework screenshots"
git push
```

Delete this file once all required screenshots exist.
