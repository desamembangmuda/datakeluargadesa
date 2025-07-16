# streamlit: title = Dashboard

import streamlit as st

st.set_page_config(page_title=" home", page_icon="🏠")


# ✅ Cek login
if "login" not in st.session_state or not st.session_state["login"]:
    st.warning("⚠️ Silakan login terlebih dahulu.")
    st.stop()

# 🌟 Tampilan dashboard
st.markdown("""
<style>
.centered {
    text-align: center;
}
.big-title {
    font-size: 2.2em;
    font-weight: bold;
    color: #2c3e50;
}
.sub-title {
    font-size: 1.5em;
    color: #16a085;
    margin-top: -10px;
}
.tip-box {
    background-color: #f9f9f9;
    border-left: 6px solid #2ecc71;
    padding: 10px 20px;
    border-radius: 5px;
    margin-top: 30px;
}
</style>

<div class="centered">
    <div class="big-title">👋 Halo, Selamat Datang di</div>
    <div class="big-title">FORM ENTRY DATA KELUARGA</div>
    <div class="sub-title">🏡 DESA MEMBANG MUDA</div>
</div>

<hr style="margin-top: 30px; margin-bottom: 20px;">

<div class="tip-box">
    <b>🛡️ Tips Keamanan:</b><br>
    Jangan lupa klik <b>Logout</b> setelah selesai menggunakan aplikasi.
</div>
""", unsafe_allow_html=True)
