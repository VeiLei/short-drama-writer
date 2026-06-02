---
name: drama-dashboard
description: Starts a read-only web dashboard to view project status, episode content, asset gallery, and character relationship graphs.
allowed-tools: Bash
---

Launch the read-only drama project dashboard.

## Workflow

### Step 1: Verify Backend

Check backend is running:
```bash
curl {BACKEND_URL}/api/health
```

If not running, start it:
```bash
cd {BACKEND_DIR} && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 &
```

### Step 2: Launch Dashboard

```bash
cd {BACKEND_DIR}/dashboard && npm run dev
```

The dashboard is a read-only React app that:
- Shows project overview (episodes written, assets generated)
- Displays character relationship graph
- Shows episode list with scene and shot breakdowns
- Previews generated images and videos
- Allows marking assets for regeneration (returns to Claude for execution)

### Step 3: Open Browser

Tell user to open `http://localhost:5173` (or the port shown in terminal output).
