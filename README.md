# TCP Chat Server

A full-stack real-time chat application built using:

- Python
- FastAPI
- React
- WebSockets
- PostgreSQL
- bcrypt Authentication

This project evolved phase-by-phase from a basic TCP socket server into a modern real-time chat system with authentication, persistent chat history, online user tracking, and responsive frontend support.

---

# Features

## Authentication
- User Registration
- User Login
- Password Hashing with bcrypt
- Duplicate Login Prevention
- PostgreSQL-backed User Storage

---

## Real-Time Communication
- Multi-client real-time messaging
- WebSocket-based communication
- Instant message synchronization
- Online users tracking
- Join/Leave system messages

---

## Persistence
- PostgreSQL database integration
- Persistent chat history
- Automatic history recovery on reconnect

---

## Frontend
- React + Vite frontend
- Responsive UI
- Mobile-friendly layout
- Inline authentication messages
- Real-time updates without refresh

---

# Tech Stack

## Backend
- Python
- FastAPI
- WebSockets
- psycopg2
- bcrypt

---

## Frontend
- React
- Vite

---

## Database
- PostgreSQL

---

# Project Structure

```text
tcp-chat-server/
│
├── client/
├── frontend/
├── server/
├── shared/
├── websocket_server/
│
├── requirements.txt
└── README.md
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/karthikeya20012007/tcp-chat-server.git
```

```bash
cd tcp-chat-server
```

---

# Backend Setup

## Create Virtual Environment

```bash
python -m venv venv
```

---

## Activate Virtual Environment

### Linux / WSL

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install fastapi uvicorn psycopg2 bcrypt python-multipart
```

---

# PostgreSQL Setup

## Create Database

```sql
CREATE DATABASE tcp_chat;
```

---

## Create Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Create Messages Table

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    sender VARCHAR(50),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# Configuration

Update database credentials inside:

```text
shared/config.py
```

Example:

```python
DB_HOST = "localhost"
DB_NAME = "tcp_chat"
DB_USER = "postgres"
DB_PASSWORD = "your_password"
```

---

# Running Backend

```bash
uvicorn websocket_server.app:app --reload --host 0.0.0.0 --port 8000
```

Backend runs on:

```text
http://localhost:8000
```

---

# Frontend Setup

```bash
cd frontend
```

---

## Install Packages

```bash
npm install
```

---

## Start Frontend

```bash
npm run dev -- --host
```

Frontend runs on:

```text
http://localhost:5173
```

---

# Usage

## Register
Create a new account using:
- Username
- Password

---

## Login
Login using registered credentials.

---

## Chat
- Send real-time messages
- View online users
- Receive chat history automatically
- Join from multiple devices on the same network

---

# Future Improvements

- JWT Authentication
- Private Chats
- Chat Rooms
- Redis Pub/Sub Scaling
- Docker Deployment
- Message Timestamps
- Typing Indicators
- Media/File Sharing
- Kubernetes Deployment
- End-to-End Encryption

---

# Learning Outcomes

This project demonstrates:

- Socket Programming
- Concurrent Systems
- WebSocket Architecture
- Full-Stack Integration
- Real-Time Systems
- Authentication Systems
- PostgreSQL Persistence
- Frontend/Backend Communication
- Responsive UI Design

---

# Author

Karthikeya

GitHub:
https://github.com/karthikeya20012007