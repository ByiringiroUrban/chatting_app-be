# 🚀 Muraho Backend API & Real-Time WebSocket Service

Muraho is the high-performance backend powering the Rwandan Messaging & Business Suite. It is built with **FastAPI**, **SQLAlchemy 2.0 (Async)**, **Neon PostgreSQL** (with automatic zero-config **SQLite** fallback), and **WebSockets** for real-time messaging, typing indicators, and WebRTC call signaling.

---

## 📋 Table of Contents
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Quick Start Guide](#-quick-start-guide)
  - [1. Navigate to Backend](#1-navigate-to-backend-directory)
  - [2. Create & Activate Virtual Environment](#2-create--activate-virtual-environment)
  - [3. Install Dependencies](#3-install-dependencies)
  - [4. Configure Environment Variables (.env)](#4-configure-environment-variables-env)
  - [5. Test Database Connection (Optional)](#5-test-database-connection-optional)
  - [6. Run the Server](#6-run-the-server)
- [Interactive API Documentation](#-interactive-api-documentation)
- [Real-Time WebSocket Protocol](#-real-time-websocket-protocol)
- [Running Automated Tests](#-running-automated-tests)
- [Database Options (SQLite vs Neon PostgreSQL)](#-database-options)
- [Troubleshooting & FAQs](#-troubleshooting--faqs)

---

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Async ASGI)
- **Server**: [Uvicorn](https://www.uvicorn.org/)
- **ORM / Database Layer**: [SQLAlchemy 2.0 Async](https://www.sqlalchemy.org/) with `asyncpg` (PostgreSQL) and `aiosqlite` (SQLite)
- **Database Options**:
  - **Neon Serverless PostgreSQL** (Production / Cloud)
  - **SQLite** (`muraho.db`) (Instant local development fallback)
- **Validation & Settings**: Pydantic v2 & Pydantic-Settings
- **Security**: JWT (`python-jose`) + password hashing with `passlib` & `bcrypt`
- **Real-Time Communication**: Native WebSockets with multi-room broadcast & typing indicators
- **File Uploads**: `python-multipart` & `aiofiles`

---

## 📂 Project Structure

```text
backend/
├── app/
│   ├── config.py              # Environment configuration & DB URL resolution
│   ├── database.py            # Async SQLAlchemy engine, session maker & init_db
│   ├── main.py                # FastAPI app entry, CORS, lifespan & WebSocket router
│   ├── seed_data.py           # Auto-seeding initial Rwandan users, chats, products
│   ├── core/
│   │   └── security.py        # Password hashing & JWT token generators
│   ├── models/                # SQLAlchemy database models
│   │   ├── user.py            # User & Contact models
│   │   ├── conversation.py    # Direct & group conversation models
│   │   ├── message.py         # Chat messages & media
│   │   ├── business.py        # Business profiles, catalog products & AI FAQ
│   │   └── ...
│   ├── routers/               # Modular REST API endpoints
│   │   ├── auth.py            # Login, registration, profile (/api/v1/auth)
│   │   ├── conversations.py   # Chat listing & creation
│   │   ├── messages.py        # Message dispatch & history
│   │   ├── groups.py          # Communities & member management
│   │   ├── statuses.py        # 24h stories
│   │   ├── channels.py        # Public & premium paid channels
│   │   ├── business.py        # Products, tickets, AI support simulator
│   │   ├── calls.py           # Call logs & WebRTC signaling
│   │   ├── subscriptions.py   # Plans & billing
│   │   └── upload.py          # Media & file attachments
│   ├── schemas/               # Pydantic request/response validation schemas
│   └── websocket/
│       └── manager.py         # Connection manager for real-time WebSockets
├── uploads/                   # Uploaded images, audio notes, and attachments
├── .env.example               # Example environment variables template
├── .env                       # Active local configuration (create from example)
├── muraho.db                  # Local SQLite database (created automatically)
├── requirements.txt           # Python dependencies
├── run.py                     # Convenience launcher script
├── test_api_endpoints.py      # Automated 14-point API integration test suite
└── test_db_connection.py      # Database diagnostic script
```

---

## ⚙️ Prerequisites

- **Python 3.10+** (Tested and verified on Python 3.12)
- **pip** package manager

Verify your Python installation by running:
```bash
python --version
```

---

## 🚀 Quick Start Guide

### 1. Navigate to Backend Directory
Open your terminal and navigate to the `backend` folder:

```bash
cd backend
```

### 2. Create & Activate Virtual Environment

#### Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> **Note for PowerShell Users:** If you see an execution policy error (`running scripts is disabled`), run this once in PowerShell:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

#### Windows (Command Prompt):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

Install all required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables (.env)

A `.env.example` file is provided. Copy it to create your active `.env`:

#### Windows:
```powershell
copy .env.example .env
```

#### macOS / Linux:
```bash
cp .env.example .env
```

#### Understanding the `.env` settings:
```env
# Database URL:
# 1. Leave as placeholder to run immediately on local SQLite (muraho.db)
# 2. Or paste your Neon PostgreSQL connection string:
DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD@ep-YOUR-ENDPOINT.neon.tech/neondb?sslmode=require

# Application settings
ENVIRONMENT=development
DEBUG=True
PORT=8000
HOST=0.0.0.0

# CORS Allowed Origins
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000

# Security / JWT
SECRET_KEY=muraho_super_secret_jwt_key_2026_kigali_tech_innovations
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Auto-seed mock data on first startup if tables are empty
AUTO_SEED=True
```

---

### 5. Test Database Connection (Optional)

You can run the included database diagnostic script to verify your connection before starting the server:

```bash
python test_db_connection.py
```

Expected output:
```text
============================================================
 Muraho Chatting App — Database Diagnostic Test
============================================================
Engine Protocol: sqlite+aiosqlite (or postgresql+asyncpg)
Attempting database handshake...
✅ CONNECTION SUCCESSFUL! (Latency: ~15ms)
============================================================
```

---

### 6. Run the Server

Start the backend application with either of the following commands:

#### Option A: Using the convenience launcher (Recommended)
```bash
python run.py
```

#### Option B: Using Uvicorn directly
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

When the server starts successfully, you will see:
```text
🚀 Starting Muraho Chatting & Business API v1.0.0
📍 Server running at: http://0.0.0.0:8000
📖 Interactive Swagger Docs: http://localhost:8000/docs
🔌 WebSocket URL: ws://localhost:8000/ws/{user_id}
[Muraho DB] Tables verified/created successfully.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 📖 Interactive API Documentation

Once the server is running, open your web browser to explore and test all endpoints interactively:

- **Swagger UI (Interactive)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc UI**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Root Status**: [http://localhost:8000/](http://localhost:8000/)

### Key API Endpoints Overview:

| Endpoint Group | Prefix | Description |
| :--- | :--- | :--- |
| **Authentication** | `/api/v1/auth` | User registration, login, token refresh, OTP |
| **Users & Contacts** | `/api/v1/users` | Profile fetch (`/me`), update profile, list contacts |
| **Conversations** | `/api/v1/conversations` | Direct & group chats list, create chat, pin chat |
| **Messages** | `/api/v1/conversations/{id}/messages` | Get message history, send new messages |
| **Groups** | `/api/v1/groups` | Rwandan developer & business communities |
| **Statuses** | `/api/v1/statuses` | 24-hour disappearing stories feed & posting |
| **Channels** | `/api/v1/channels` | Discover channels, broadcast messages, subscriptions |
| **Business Suite**| `/api/v1/business` | Product catalog in RWF, customer tickets, AI simulator |
| **Calls** | `/api/v1/calls` | Call history log & duration tracking |
| **Subscriptions** | `/api/v1/subscriptions` | Pricing tiers (Free, Premium, Business, AI) |
| **Uploads** | `/api/v1/upload` | File attachments, voice notes, photos |

---

## 🔌 Real-Time WebSocket Protocol

Muraho includes a native WebSocket server for bidirectional real-time communication:

- **WebSocket URL**: `ws://localhost:8000/ws/{user_id}`

### Supported Events:

1. **Typing Indicators**:
   - Send: `{"event": "chat.typing", "data": {"conversationId": "conv_1", "isTyping": true}}`
   - Broadcasts typing state to other participants in the conversation.

2. **Room Management**:
   - Join: `{"event": "room.join", "data": {"conversationId": "conv_1"}}`
   - Leave: `{"event": "room.leave", "data": {"conversationId": "conv_1"}}`

3. **WebRTC Video & Voice Call Signaling**:
   - Handles `call.offer`, `call.answer`, `call.ice_candidate`, `call.reject`, `call.end`.
   - Routes signaling payloads directly to `targetUserId`.

---

## 🧪 Running Automated Tests

A comprehensive integration test suite is included in `test_api_endpoints.py`. It tests all 14 core API services:

```bash
python test_api_endpoints.py
```

Expected result:
```text
============================================================
 Muraho Backend API Integration Test Suite
============================================================
 [PASS] 1. GET /health -> 200 OK
 [PASS] 2. GET /api/v1/users/me -> Jean-Luc Mugisha (@jeanluc_m)
 [PASS] 3. GET /api/v1/users/contacts -> 6 contacts
 [PASS] 4. GET /api/v1/conversations -> 6 active conversations
 [PASS] 5. GET /api/v1/conversations/conv_1/messages -> 5 messages in thread
 [PASS] 6. POST /api/v1/conversations/conv_1/messages -> Sent message ID
 [PASS] 7. GET /api/v1/groups -> 2 Rwandan tech communities
 [PASS] 8. GET /api/v1/statuses/feed -> 2 stories loaded
 [PASS] 9. GET /api/v1/channels -> 2 channels loaded
 [PASS] 10. GET /api/v1/business/profile -> Kigali Tech Innovations & Artisans Ltd
 [PASS] 11. GET /api/v1/business/catalog -> 6 products priced in RWF
 [PASS] 12. POST /api/v1/business/ai-support/test -> Confidence: 0.92
 [PASS] 13. GET /api/v1/calls/history -> 2 calls in log
 [PASS] 14. GET /api/v1/subscriptions/plans -> 4 plans available
============================================================
 ALL 14 TEST SUITES PASSED FLAWLESSLY! 
============================================================
```

---

## 🗄️ Database Options

### Option 1: Instant Local SQLite (Default)
- **No external accounts or cloud setup needed**.
- If `DATABASE_URL` in `.env` is empty or contains `YOUR_NEON_PASSWORD`, the server automatically initializes `muraho.db` locally.
- Tables are generated and populated with initial mock data on first startup.

### Option 2: Neon Serverless PostgreSQL (Cloud)
1. Sign up for free at [Neon Console](https://console.neon.tech).
2. Create a new project and copy your connection string.
3. Update `DATABASE_URL` in `backend/.env`:
   ```env
   DATABASE_URL=postgresql://neondb_owner:YOUR_ACTUAL_PASSWORD@ep-cool-sun-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. Run `python test_db_connection.py` to test connectivity.

---

## ❓ Troubleshooting & FAQs

### 1. `uvicorn: command not found` or `ModuleNotFoundError`
Ensure you have activated your virtual environment before running Python commands:
- Windows: `.\venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`
- Run `pip install -r requirements.txt`

### 2. `Address already in use` (Port 8000 conflict)
If another process is using port 8000:
- Specify an alternative port:
  ```bash
  uvicorn app.main:app --port 8080 --reload
  ```
- Or change `PORT=8080` in `.env`.

### 3. Frontend connection (CORS error)
If your frontend runs on a different port (e.g. `http://localhost:5173` for Vite):
- Check `CORS_ORIGINS` in `.env` and verify it contains your frontend's URL. By default, CORS is configured to accept requests from standard Vite and React development ports.

---

## 🤝 Connecting to the Frontend

The frontend React application is located in the root directory. To run both concurrently:

1. **Backend** (Terminal 1):
   ```bash
   cd backend
   python run.py
   ```
2. **Frontend** (Terminal 2):
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` to view the full application.
