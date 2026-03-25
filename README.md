# 🚀 AIIR SOW Automation System

Automated Statement of Work (SOW) generation from discovery call transcripts using AI.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [Railway Deployment](#railway-deployment)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The AIIR SOW Automation System automates the entire process of generating Statements of Work from discovery call transcripts:

1. **Transcript Processing**: Upload transcript → AI extracts variables
2. **Pricing Calculation**: Automated pricing based on business logic
3. **Document Generation**: Creates SOW and pricing calculator
4. **Approval Workflow**: Email notifications with approval webhooks
5. **Client Delivery**: Automated document delivery to clients

---

## ✨ Features

- 🤖 **AI-Powered Extraction**: OpenAI GPT extracts variables from transcripts
- 📊 **Automated Pricing**: Complex pricing calculator with 360-degree tier logic
- 📝 **Document Generation**: SOW and pricing sheets in Google Docs/Sheets
- 📧 **Email Notifications**: Automated emails with approval workflows
- 🔄 **Webhook Integration**: n8n workflow automation via webhooks
- 📈 **Progress Tracking**: Google Sheets tracker for all engagements
- ☁️ **Cloud Storage**: Google Drive integration for all documents

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Google Drive   │ ← Transcript uploaded
│   (n8n Watch)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI App    │
│  (Railway)      │
├─────────────────┤
│ • Webhooks      │
│ • Business Logic│
│ • AI Processing │
└────────┬────────┘
         │
         ├──────────► OpenAI API (Extract variables)
         │
         ├──────────► Google Sheets (Tracker + Calculator)
         │
         ├──────────► Google Docs (SOW generation)
         │
         ├──────────► Gmail (Send notifications)
         │
         └──────────► Upstash Redis (State management)
```

---

## 📦 Prerequisites

- **Python 3.11+**
- **Google Cloud Platform Account**
  - Service Account with Drive, Sheets, Docs, Gmail APIs enabled
  - Service Account JSON key file
- **OpenAI API Key** (GPT-4 recommended)
- **Upstash Redis** (Free tier works)
- **Railway Account** (for deployment)
- **n8n Instance** (for workflow automation)

---

## 🔧 Local Setup

### 1. Clone Repository

```bash
git clone https://github.com/Realine-support/AIIR-SOW-System.git
cd AIIR-SOW-System/aiir-sow-system
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your actual values
```

See [Environment Variables](#environment-variables) section for details.

### 5. Add Google Service Account Credentials

```bash
# Place your service account JSON file in the project root
# Update GOOGLE_CREDENTIALS_PATH in .env to point to this file
```

### 6. Run Local Server

```bash
cd aiir-sow-system
python -m uvicorn api.index:app --reload --host 0.0.0.0 --port 8000
```

### 7. Verify Installation

Visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🚂 Railway Deployment

### Prerequisites

1. **Delete old Railway service** (if exists):
   - Go to Railway Dashboard
   - Settings → Delete Service
   - This clears all cached builds

### Step-by-Step Deployment

#### 1. Create New Railway Service

```bash
# Push latest code to GitHub first
git push origin master

# In Railway Dashboard:
# 1. Click "New Project"
# 2. Select "Deploy from GitHub repo"
# 3. Choose: Realine-support/AIIR-SOW-System
# 4. Railway auto-detects Dockerfile ✅
```

#### 2. Configure Environment Variables

In Railway Dashboard → Variables tab, add ALL variables from `.env.example`:

**Required Variables:**
```
OPENAI_API_KEY=sk-proj-xxxxx
GOOGLE_SERVICE_ACCOUNT_EMAIL=xxx@xxx.iam.gserviceaccount.com
TRACKER_SHEET_ID=1XXXXxxxx
... (see .env.example for complete list)
```

**IMPORTANT: Google Credentials**

Railway requires credentials as environment variable (not file):

```bash
# Convert your service account JSON to single-line string
cat service-account.json | jq -c

# In Railway, create variable:
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}
```

**Update [`app/config.py`](aiir-sow-system/app/config.py)** to use JSON string:

```python
# Change from:
google_credentials_path: str

# To:
google_credentials_json: str
```

#### 3. Set Production Configuration

```
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
BASE_URL=https://your-app.railway.app
```

#### 4. Deploy

```bash
# Railway auto-deploys on git push
git add .
git commit -m "Production deployment"
git push origin master

# Monitor deployment in Railway Dashboard
# Build time: ~3-5 minutes
```

#### 5. Verify Deployment

```bash
# Check health endpoint
curl https://your-app.railway.app/health

# Expected response:
{
  "status": "healthy",
  "service": "AIIR SOW Automation System",
  "version": "1.0.0"
}
```

---

## 🔐 Environment Variables

See [`.env.example`](aiir-sow-system/.env.example) for complete list.

### Critical Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-xxxxx` |
| `GOOGLE_CREDENTIALS_JSON` | Service account JSON (one-line) | `{"type":"service_account",...}` |
| `TRACKER_SHEET_ID` | Google Sheets tracker ID | `1ABCDxxxxxx` |
| `UPSTASH_REDIS_REST_URL` | Redis URL | `https://xxx.upstash.io` |
| `BASE_URL` | Your Railway app URL | `https://your-app.railway.app` |
| `ENVIRONMENT` | `production` or `development` | `production` |

---

## 📡 API Endpoints

### Health Checks

- `GET /` - Basic health check
- `GET /health` - Detailed health check with all endpoints

### Webhooks

- `POST /webhooks/google-drive-file-added` - New transcript uploaded
- `POST /webhooks/pricing-model-approved` - Pricing approved
- `POST /webhooks/approve-pricing` - Approve pricing webhook
- `POST /webhooks/approve-sow` - Approve SOW webhook

### Cron Jobs

- `GET /cron/watch-transcripts` - Watch for new transcripts

### Interactive Documentation

Visit `/docs` for Swagger UI with interactive API testing.

---

## 🧪 Testing

### Run All Tests

```bash
cd aiir-sow-system
pytest -v
```

### Run Specific Test

```bash
pytest test_webhook.py -v
pytest test_business_logic.py -v
```

### Test Coverage

```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html
```

---

## 🔍 Troubleshooting

### Issue: Railway Build Fails with pydantic Error

**Solution:**
```bash
# Delete Railway service completely
# Create fresh service (clears cache)
# Ensure requirements.txt has: pydantic==2.8.0
```

### Issue: Google API Authentication Failed

**Solution:**
```bash
# Verify service account has correct permissions:
# - Google Drive API enabled
# - Google Sheets API enabled
# - Google Docs API enabled
# - Gmail API enabled (if sending emails)

# Check service account email is correct
# Verify GOOGLE_CREDENTIALS_JSON is valid JSON
```

### Issue: Environment Variables Not Loading

**Solution:**
```bash
# In Railway, verify ALL variables from .env.example are set
# Check for typos in variable names (case-sensitive)
# Restart deployment after adding variables
```

### Issue: Webhook Not Receiving Requests

**Solution:**
```bash
# Verify BASE_URL is correct Railway URL
# Check n8n webhook URL matches Railway deployment
# Ensure Railway service is running (check logs)
```

---

## 📊 Monitoring

### Railway Logs

```bash
# View real-time logs in Railway Dashboard
# Or use Railway CLI:
railway logs
```

### Health Check Endpoint

```bash
# Automated monitoring
curl https://your-app.railway.app/health
```

---

## 🛠️ Development

### Project Structure

```
aiir-sow-system/
├── api/
│   ├── index.py           # Main FastAPI app
│   ├── webhooks/          # Webhook endpoints
│   └── cron/              # Cron job endpoints
├── app/
│   ├── business_logic/    # Pricing calculations
│   ├── models/            # Pydantic models
│   ├── services/          # External API integrations
│   ├── workflows/         # End-to-end workflows
│   └── config.py          # Configuration management
├── tests/                 # Test files
├── requirements.txt       # Python dependencies
└── .env.example          # Environment template
```

---

## 📝 License

MIT License - see LICENSE file for details.

---

## 🤝 Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review Railway deployment logs
3. Create an issue in GitHub repository

---

## 🚀 Quick Start Checklist

- [ ] Clone repository
- [ ] Install Python 3.11+
- [ ] Copy `.env.example` to `.env`
- [ ] Fill in all environment variables
- [ ] Add Google service account JSON
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run locally: `python -m uvicorn api.index:app --reload`
- [ ] Test endpoint: `http://localhost:8000/health`
- [ ] Delete old Railway service (if exists)
- [ ] Create new Railway service from GitHub
- [ ] Add all environment variables in Railway
- [ ] Deploy and verify: `curl https://your-app.railway.app/health`

**You're ready to go!** 🎉
