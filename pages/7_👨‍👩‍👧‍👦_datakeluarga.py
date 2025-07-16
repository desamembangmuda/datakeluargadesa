import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Cek login dan isi KK
if "login" not in st.session_state or not st.session_state["login"]:
    st.warning("⚠️ Silakan login terlebih dahulu.")
    st.stop()

if "no_kk" not in st.session_state:
    st.warning("⚠️ Silakan isi Form Keluarga terlebih dahulu.")
    st.stop()

# Koneksi ke Google Sheets
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
    client = gspread.authorize(creds)
    return client.open_by_key("1LOv15OJL__vKiok8qmJqPGt4Je4nmxVSV0_a0ed8L5w").worksheet("Anggota")

# Ambil data semua anggota
def ambil_semua_data():
    sheet = get_sheet()
    records = sheet.get_all_values()
    df = pd.DataFrame(records[1:], columns=[col.lower() for col in records[0]])
    return df

# Tampilan halaman
st.set_page_config(page_title="Data Anggota Keluarga", layout="wide")
st.title("📋 Data Anggota Keluarga")

try:
    df = ambil_semua_data()
    # Filter berdasarkan No KK user
    df = df[df['no kk'].str.strip() == st.session_state.no_kk]

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Belum ada data anggota keluarga.")
except Exception as e:
    st.error(f"❌ Gagal mengambil data: {e}")
