
import streamlit as st
import os
import json
import time
import hashlib
from datetime import datetime
from PIL import *

USERS_FILE = "users.json"
CHAT_FILE = "chat_data.json"
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)
for file in [USERS_FILE, CHAT_FILE]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([] if "chat" in file else {}, f)

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def load_chat():
    with open(CHAT_FILE, "r") as f:
        return json.load(f)

def save_chat(data):
    with open(CHAT_FILE, "w") as f:
        json.dump(data, f)

def add_message(user, message, msg_type="text"):
    data = load_chat()
    data.append({"user": user, "message": message, "type": msg_type, "time": datetime.now().strftime("%H:%M")})
    save_chat(data)

st.sidebar.title("🔐 Login / Register")
mode = st.sidebar.radio("Choose mode", ["Login", "Register"])

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if mode == "Register":
    if st.sidebar.button("Register"):
        users = load_users()
        if username in users:
            st.sidebar.warning("Username already exists.")
        else:
            users[username] = hash_pw(password)
            save_users(users)
            st.sidebar.success("Registered! Please login.")
elif mode == "Login":
    if st.sidebar.button("Login"):
        users = load_users()
        if username in users and users[username] == hash_pw(password):
            st.session_state["user"] = username
            st.sidebar.success(f"Welcome, {username}!")
        else:
            st.sidebar.error("Invalid credentials")

if "user" in st.session_state:
    st.title("💬 Chat room")
    st.markdown(f"👋 Logged in as **{st.session_state['user']}**")

    uploaded = st.file_uploader("Upload image or file", type=["png", "jpg", "jpeg", "pdf", "txt"])
    if uploaded:
        filepath = os.path.join(UPLOAD_DIR, uploaded.name)
        with open(filepath, "wb") as f:
            f.write(uploaded.read())
        add_message(st.session_state['user'], filepath, msg_type="file")
        st.success("Uploaded and sent!")

    with st.form("send_message", clear_on_submit=True):
        msg = st.text_input("Type a message")
        submitted = st.form_submit_button("Send")
        if submitted and msg:
            add_message(st.session_state['user'], msg)

    st.markdown("---")
    st.markdown("### 📜 Chat Messages")
    messages = load_chat()
    for m in messages:
        is_user = m["user"] == st.session_state['user']
        if m["type"] == "text":
            st.markdown(f"<div style='background:{'#dcf8c6' if is_user else '#fff'};padding:10px;border-radius:8px;margin:5px 0'><b>{m['user']}:</b> {m['message']} <small>({m['time']})</small></div>", unsafe_allow_html=True)
        elif m["type"] == "file":
            file_name = os.path.basename(m["message"])
            if file_name.endswith(('.png', '.jpg', '.jpeg')):
                st.image(m["message"], caption=f"{m['user']} ({m['time']})", width=150)
            else:
                st.markdown(f"📄 [{file_name}]({m['message']}) from **{m['user']}** ({m['time']})")

    if st.session_state['user'].lower() == "saad":
        if st.button("🗑️ Clear All Messages"):
            save_chat([])
            st.success("Chat cleared!")
else:
    st.warning("Please login or register to use the app.")

st.table([
    {"Feature": "User Authentication", "Status": "✅"},
    {"Feature": "Chat Messages", "Status": "✅"},
    {"Feature": "File Upload", "Status": "✅"},
    {"Feature": "Image Display", "Status": "✅"},
    {"Feature": "Chat History", "Status": "✅"},
    {"Feature": "Admin Controls", "Status": "✅ (Admin only)"},

])


