import os
import json
import psycopg2
import bcrypt
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import local fallbacks
from shared.config import (
    DB_HOST,
    DB_NAME,
    DB_USER,
    DB_PASSWORD
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuthRequest(BaseModel):
    username: str
    password: str

connected_clients = {}

# Fallback Logic: Live Environment variables take precedence over local configuration
LIVE_HOST = os.environ.get("DB_HOST") or DB_HOST
LIVE_NAME = os.environ.get("DB_NAME") or DB_NAME
LIVE_USER = os.environ.get("DB_USER") or DB_USER
LIVE_PASS = os.environ.get("DB_PASSWORD") or DB_PASSWORD

connection = None

try:
    print(f"🔄 Connecting to database host: {LIVE_HOST} as user: {LIVE_USER}...")
    connection = psycopg2.connect(
        host=LIVE_HOST,
        database=LIVE_NAME,
        user=LIVE_USER,
        password=LIVE_PASS,
        sslmode="require"
    )
    print("✅ Connected to the database successfully!")
except psycopg2.OperationalError as e:
    print("❌ Database connection failed during startup!")
    print(f"Error Details: {e}")


def save_message(sender, content):
    if not connection:
        print("❌ Cannot save message: Database connection is down.")
        return
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO messages (sender, content)
                VALUES (%s, %s)
            """, (sender, content))
            connection.commit()
    except Exception as e:
        print(f"❌ Error saving message: {e}")
        connection.rollback()


async def send_chat_history(websocket):
    if not connection:
        return
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sender, content
                FROM messages
                ORDER BY id ASC
            """)
            messages = cursor.fetchall()

        for sender, content in messages:
            history_message = {
                "type": "history",
                "message": f"{sender}: {content}"
            }
            await websocket.send_text(json.dumps(history_message))
    except Exception as e:
        print(f"❌ Error fetching chat history: {e}")


async def broadcast_online_users():
    users_message = {
        "type": "users",
        "users": list(connected_clients.values())
    }
    for client in connected_clients.copy():
        try:
            await client.send_text(json.dumps(users_message))
        except:
            if client in connected_clients:
                del connected_clients[client]


async def broadcast_chat_message(message):
    for client in connected_clients.copy():
        try:
            await client.send_text(json.dumps(message))
        except:
            if client in connected_clients:
                del connected_clients[client]


@app.post("/register")
def register(data: AuthRequest):
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection unavailable")
    
    username = data.username
    password = data.password

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT username FROM users WHERE username = %s
            """, (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                raise HTTPException(status_code=400, detail="Username already exists")

            hashed_password = bcrypt.hashpw(
                password.encode(),
                bcrypt.gensalt()
            ).decode()

            cursor.execute("""
                INSERT INTO users (username, password_hash)
                VALUES (%s, %s)
            """, (username, hashed_password))
            connection.commit()
            
        return {"message": "Registration successful"}
    except HTTPException:
        raise
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    

@app.post("/login")
def login(data: AuthRequest):
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection unavailable")

    username = data.username
    password = data.password

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT password_hash FROM users WHERE username = %s
            """, (username,))
            user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid username")

        stored_password = user[0]

        if not bcrypt.checkpw(password.encode(), stored_password.encode()):
            raise HTTPException(status_code=401, detail="Invalid password")
            
        if username in connected_clients.values():
            raise HTTPException(status_code=400, detail="User already logged in")

        return {"message": "Login successful"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    print("✅ WebSocket accepted")

    username = None

    try:
        while True:
            raw_data = await websocket.receive_text()

            print("📩 Raw data:", raw_data)

            data = json.loads(raw_data)

            message_type = data.get("type")

            if message_type == "join":
                username = data.get("username")

                connected_clients[websocket] = username

                print(f"[CONNECTED] {username}")

                await send_chat_history(websocket)

                await broadcast_online_users()

                join_message = {
                    "type": "chat",
                    "message": f"{username} joined the chat"
                }

                await broadcast_chat_message(join_message)

            elif message_type == "chat":
                sender = data.get("username")

                content = data.get("content")

                print(f"[MESSAGE] {sender}: {content}")

                save_message(sender, content)

                chat_message = {
                    "type": "chat",
                    "message": f"{sender}: {content}"
                }

                await broadcast_chat_message(chat_message)

    except WebSocketDisconnect:
        print("❌ WebSocket disconnected")

        if websocket in connected_clients:
            disconnected_user = connected_clients[websocket]

            del connected_clients[websocket]

            leave_message = {
                "type": "chat",
                "message": f"{disconnected_user} left the chat"
            }

            await broadcast_chat_message(leave_message)

            await broadcast_online_users()

    except Exception as e:
        print("🔥 WebSocket error:", e)
        
        
@app.get("/")
async def root():
    return {"status": "running"}