# Render Free-Tier Deployment Specification

## Executive Overview
This document specifies how to deploy **IntegrationOps AI Copilot** to [Render](https://render.com) using its free tier.

The application consists of two decoupled services:
1. **FastAPI Backend**: Render Web Service (Python Runtime)
2. **React Frontend**: Render Static Site (Node/Vite Build)

---

## 1. Automated Blueprint Deployment (`render.yaml`)

The repository includes a [`render.yaml`](file:///C:/Users/kraje/.gemini/antigravity-ide/scratch/integrationops-ai/render.yaml) Blueprint file. 

To deploy both services automatically:
1. Push your repository to GitHub.
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** ➔ **Blueprint**.
4. Connect your GitHub repository (`integrationops-ai-copilot`).
5. Render will automatically detect `render.yaml` and provision both services.

---

## 2. Manual Service Configuration Guide

### Backend: Render Web Service

- **Service Type**: Web Service
- **Name**: `integrationops-backend`
- **Environment**: `Python 3`
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path**: `/health`

#### Required Environment Variables

| Variable | Value | Notes |
|---|---|---|
| `PORT` | *(Auto-assigned)* | Injected automatically by Render (e.g. `10000`). |
| `HOST` | `0.0.0.0` | Binds server to all network interfaces. |
| `ENVIRONMENT` | `production` | Sets application mode to production. |
| `LOG_LEVEL` | `INFO` | Configures structured logging. |
| `DATA_DIR` | `./data` | Relative path to synthetic datasets & docs. |
| `LLM_PROVIDER` | `mock` | Uses offline fallback mode (set to `openai` or `gemini` if providing API keys). |
| `CORS_ORIGINS` | `*` | Permits cross-origin requests from the React frontend. |

---

### Frontend: Render Static Site

- **Service Type**: Static Site
- **Name**: `integrationops-frontend`
- **Root Directory**: `frontend`
- **Build Command**: `npm install && npm run build`
- **Publish Directory**: `dist`

#### Required Environment Variables

| Variable | Value | Notes |
|---|---|---|
| `VITE_API_BASE_URL` | `https://integrationops-backend.onrender.com` | Set to your live backend Render Web Service URL. |

---

## 3. Free-Tier Behavioral & Operational Limitations

> [!WARNING]
> **Free-Tier Cold Start Delay**: On Render's free tier, Web Services automatically enter a sleeping state after 15 minutes of inactivity. When a new HTTP request (`POST /ask`) arrives after a sleep period, Render takes approximately **30 to 50 seconds** to wake up the Python process. Subsequent requests respond instantly (1.5 ms).

- **Portfolio & Demo Scope**: This project is engineered as an independent technical portfolio demonstration showcasing RAG architecture, agent design, and MCP concepts, rather than a high-availability production enterprise product.
- **In-Memory Volatility**: Vector indexes and synthetic data repositories load directly into memory upon server startup with zero external database dependencies.
