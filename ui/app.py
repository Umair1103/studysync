import streamlit as st
import requests
import websocket
import threading
import time
from pathlib import Path
import sys
import os

# ---------------------- AI MODULE SETUP ----------------------
sys.path.append(str(Path(__file__).resolve().parents[1] / "ai"))
import importlib.util

ai_path = Path(__file__).resolve().parents[1] / "ai" / "ai_app.py"
spec = importlib.util.spec_from_file_location("ai_app", str(ai_path))
ai_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_app)

process_file = ai_app.process_file
ask_question = ai_app.ask_question

# ---------------------- STREAMLIT UI ----------------------
st.title("StudySync AI – Complete System")

# ---------------------- AI UPLOAD & QUESTION ----------------------
st.header("Upload Notes for AI Assistant")

uploaded_file = st.file_uploader("Upload PDF")

if "doc_uploaded" not in st.session_state:
    st.session_state.doc_uploaded = False

if uploaded_file is not None:
    folder = "ai/uploads"
    os.makedirs(folder, exist_ok=True)
    path = f"{folder}/{uploaded_file.name}"

    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    process_file(path)
    st.session_state.doc_uploaded = True
    st.success("Document processed! You can now ask questions.")

question = st.text_input("Ask your question (general or PDF-based)")

if st.button("Ask"):
    if question.strip() == "":
        st.error("Please enter a question.")
    else:
        with st.spinner("Processing..."):
            reply = ask_question(question)
        st.write(reply)

# ============================================================
# 🔥 MULTI USER CHAT (PURE WEBSOCKET)
# ============================================================

st.header("Online Multi-User Chat")

# 🔴 CHANGE THIS TO YOUR NGROK URL (WITHOUT https://)
BACKEND_HOST = "ofelia-prouniversity-filmily.ngrok-free.dev"

# Session state
if "ws" not in st.session_state:
    st.session_state.ws = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "room_id" not in st.session_state:
    st.session_state.room_id = None


# ---------------------- CREATE ROOM ----------------------
if st.button("Create New Chat Room"):
    try:
        res = requests.get(f"https://{BACKEND_HOST}/create_room")
        data = res.json()

        st.session_state.room_id = data["room_id"]

        st.success("Room created successfully!")
        st.write("Room ID (share this with others):")
        st.code(data["room_id"])

    except Exception as e:
        st.error(f"Error creating room: {e}")


# ---------------------- JOIN ROOM ----------------------
room_id_input = st.text_input("Enter Room ID to Join Chat")

def receive_messages():
    ws = st.session_state.ws
    try:
        while True:
            msg = ws.recv()
            st.session_state.messages.append(msg)
            time.sleep(0.1)
    except:
        pass


if st.button("Join Chat"):
    if room_id_input.strip() == "":
        st.error("Please enter a valid Room ID.")
    else:
        try:
            ws_url = f"wss://{BACKEND_HOST}/ws/{room_id_input}"

            ws = websocket.WebSocket()
            ws.connect(ws_url)

            st.session_state.ws = ws
            st.session_state.room_id = room_id_input

            threading.Thread(target=receive_messages, daemon=True).start()

            st.success(f"Joined room {room_id_input}")

        except Exception as e:
            st.error(f"Error connecting to chat server: {e}")


# ---------------------- DISPLAY MESSAGES ----------------------
st.subheader("Messages")

for msg in st.session_state.messages:
    st.write(msg)


# ---------------------- SEND MESSAGE ----------------------
msg = st.text_input("Write a message")

if st.button("Send"):
    if st.session_state.ws:
        try:
            st.session_state.ws.send(msg)
            st.session_state.messages.append(f"You: {msg}")
        except Exception as e:
            st.error(f"Failed to send message: {e}")
    else:
        st.error("You are not connected to any chat room.")
