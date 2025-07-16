import streamlit as st

st.set_page_config(page_title="Logout", page_icon="🚪")
st.markdown("# 🔓 Logout")

# Clear all session state
st.session_state.clear()
st.success("✅ Anda berhasil logout.")
st.switch_page("login.py")