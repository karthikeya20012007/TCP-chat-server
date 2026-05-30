from fastapi import FastAPI
from fastapi.websockets import WebSocket
from fastapi.websockets import WebSocketDisconnect

from fastapi import HTTPException
from pydantic import BaseModel
import bcrypt

import json

from fastapi.middleware.cors import CORSMiddleware

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

import os
import psycopg2

connection = psycopg2.connect(
    host=os.environ.get("DB_HOST"),
    database=os.environ.get("DB_NAME"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    sslmode="require"
)

cursor = connection.cursor()


def save_message(sender, content):
    cursor.execute("""
        INSERT INTO messages (
            sender,
            content
        )
        VALUES (%s, %s)
    """, (sender, content))

    connection.commit()


async def send_chat_history(websocket):
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

        await websocket.send_text(
            json.dumps(history_message)
        )


async def broadcast_online_users():
    users_message = {
        "type": "users",
        "users": list(
            connected_clients.values()
        )
    }

    for client in connected_clients.copy():
        try:
            await client.send_text(
                json.dumps(users_message)
            )

        except:
            del connected_clients[client]


async def broadcast_chat_message(message):
    for client in connected_clients.copy():
        try:
            await client.send_text(
                json.dumps(message)
            )

        except:
            del connected_clients[client]

@app.post("/register")
def register(data: AuthRequest):
    username = data.username
    password = data.password

    cursor.execute("""
        SELECT *
        FROM users
        WHERE username = %s
    """, (username,))

    existing_user = cursor.fetchone()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    hashed_password = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

    cursor.execute("""
        INSERT INTO users (
            username,
            password_hash
        )
        VALUES (%s, %s)
    """, (
        username,
        hashed_password
    ))

    connection.commit()

    return {
        "message": "Registration successful"
    }
    
@app.post("/login")
def login(data: AuthRequest):
    username = data.username
    password = data.password

    cursor.execute("""
        SELECT password_hash
        FROM users
        WHERE username = %s
    """, (username,))

    user = cursor.fetchone()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username"
        )

    stored_password = user[0]

    if not bcrypt.checkpw(
        password.encode(),
        stored_password.encode()
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )
        
    if username in connected_clients.values():
        raise HTTPException(
            status_code=400,
            detail="User already logged in"
        )

    return {
        "message": "Login successful"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    username = None

    try:
        while True:
            raw_data = await websocket.receive_text()

            data = json.loads(raw_data)

            message_type = data["type"]

            if message_type == "join":
                username = data["username"]

                connected_clients[websocket] = username

                print(
                    f"[CONNECTED] {username}"
                )

                await send_chat_history(
                    websocket
                )

                await broadcast_online_users()
                
                join_message = {
                    "type": "chat",
                    "message": f"{username} joined the chat"
                }

                await broadcast_chat_message(
                    join_message
                )

            elif message_type == "chat":
                sender = data["username"]

                content = data["content"]

                print(
                    f"[MESSAGE] {sender}: {content}"
                )

                save_message(
                    sender,
                    content
                )

                chat_message = {
                    "type": "chat",
                    "message": f"{sender}: {content}"
                }

                await broadcast_chat_message(
                    chat_message
                )

    except WebSocketDisconnect:
        if websocket in connected_clients:
            disconnected_user = connected_clients[
                websocket
            ]

            print(
                f"[DISCONNECTED] {disconnected_user}"
            )

            del connected_clients[websocket]
            
            leave_message = {
                "type": "chat",
                "message": f"{disconnected_user} left the chat"
            }

            await broadcast_chat_message(
                leave_message
            )

            await broadcast_online_users()