import streamlit as st
import yaml
import os
import bcrypt

# ============================
# 🔒 Fungsi untuk hash & cek
# ============================
def load_credentials():
    path = os.path.join("config", "users.yaml")
    with open(path, "r") as file:
        data = yaml.safe_load(file)
    return data["users"]

def login(username, password, users):
    if username in users:
        stored_hash = users[username]["password"]
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            return True, users[username]["name"]
    return False, None


# ============================
# 🚨 Redirect jika sudah login
# ============================
if st.session_state.get("login"):
    st.switch_page("pages/1_🏠_home.py")

# ============================
# 🖼️ Tampilan login
# ============================
st.set_page_config(page_title="🔐 LOGIN", layout="centered")
st.title("🔐 Login Aplikasi")

users = load_credentials()

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.form_submit_button("Login")

if login_btn:
    success, name = login(username, password, users)
    if success:
        st.session_state["login"] = True
        st.session_state["username"] = username
        st.session_state["name"] = name
        st.success(f"✅ Selamat datang, {name}!")
        st.switch_page("pages/1_🏠_home.py")
    else:
        st.error("❌ Username atau password salah.")
