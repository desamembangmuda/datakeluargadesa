import streamlit as st
import gspread
import pandas as pd
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Cari Anggota", layout="centered")
st.title("🔍 Cari Anggota Berdasarkan Nomor KK")

# --- Cek Login ---
if "login" not in st.session_state or not st.session_state["login"]:
    st.warning("⚠️ Silakan login terlebih dahulu.")
    st.stop()

# --- Verifikasi secrets ---
try:
    st.write("🔐 Service Account:", st.secrets["GOOGLE_SERVICE_ACCOUNT"]["client_email"])
except Exception as e:
    st.error("❌ Tidak bisa akses secret GOOGLE_SERVICE_ACCOUNT.")
    st.code(str(e))
    st.stop()

# --- Setup Koneksi ke Google Sheet ---
def get_worksheet(sheet_url, worksheet_name):
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["GOOGLE_SERVICE_ACCOUNT"], scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(sheet_url)
        return sheet.worksheet(worksheet_name)
    except Exception as e:
        st.error(f"❌ Gagal mengakses Google Sheet: {worksheet_name}")
        st.code(str(e))
        return None

# --- Fungsi ambil data dari sheet ---
def ambil_data(worksheet):
    try:
        data = worksheet.get_all_values()
        if len(data) < 2:
            return pd.DataFrame()
        df = pd.DataFrame(data[1:], columns=[c.lower().strip() for c in data[0]])
        if "no kk" in df.columns:
            df["no kk"] = df["no kk"].astype(str).str.strip()
        return df
    except Exception as e:
        st.error("❌ Gagal memuat data dari worksheet.")
        st.code(str(e))
        return pd.DataFrame()

# --- Hapus berdasarkan NIK ---
def hapus_berdasarkan_nik(nik):
    try:
        ws = get_worksheet(sheet_url, "Anggota")
        nik_col = ws.col_values(5)
        for i, val in enumerate(nik_col):
            if val.strip() == nik:
                ws.delete_rows(i + 1)
                return True
    except Exception as e:
        st.error("❌ Gagal menghapus data.")
        st.code(str(e))
    return False

# --- URL Sheet dan Nama Worksheet ---
sheet_url = "https://docs.google.com/spreadsheets/d/1OjCLeZmypzFvThwmKF2PjheHU2NKedQbw9qzt8joKvs/edit"

# --- Form Input KK ---
with st.form("form_search"):
    no_kk_input = st.text_input("Masukkan Nomor KK", max_chars=16)
    cari = st.form_submit_button("🔎 Cari")

if no_kk_input:
    ws_keluarga = get_worksheet(sheet_url, "Keluarga")
    ws_anggota = get_worksheet(sheet_url, "Anggota")

    df_keluarga = ambil_data(ws_keluarga) if ws_keluarga else pd.DataFrame()
    df_anggota = ambil_data(ws_anggota) if ws_anggota else pd.DataFrame()

    hasil_keluarga = df_keluarga[df_keluarga["no kk"] == no_kk_input.strip()]
    hasil_anggota = df_anggota[df_anggota["no kk"] == no_kk_input.strip()]
    nama_kk = hasil_keluarga.iloc[0]["nama kepala keluarga"] if not hasil_keluarga.empty else ""

    if not hasil_anggota.empty:
        st.subheader("📋 Daftar Anggota")
        for _, row in hasil_anggota.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.markdown(f"**{row['nama']}** — NIK: {row['nik']} — {row['shdk']}")
                with col2:
                    if st.button("✏️ Edit", key=f"edit_{row['nik']}"):
                        st.session_state.no_kk = row["no kk"]
                        st.session_state.nama_kk = nama_kk
                        st.session_state.edit_mode = True
                        st.session_state.edit_data = row.to_dict()
                        st.switch_page("pages/2_👪_form_anggota.py")
                with col3:
                    if st.button("🗑️ Hapus", key=f"hapus_{row['nik']}"):
                        st.session_state.konfirmasi_hapus_nik = row["nik"]
                        st.rerun()
                with col4:
                    if st.button("➕ Tambah", key=f"add_{row['nik']}"):
                        st.session_state.no_kk = no_kk_input
                        st.session_state.nama_kk = nama_kk
                        st.session_state.edit_mode = False
                        st.switch_page("pages/2_👪_form_anggota.py")
    else:
        st.warning("❗ KK valid tapi belum memiliki data anggota.")
        if st.button("➕ Tambah Anggota Baru"):
            st.session_state.no_kk = no_kk_input
            st.session_state.nama_kk = nama_kk
            st.session_state.edit_mode = False
            st.switch_page("pages/2_👪_form_anggota.py")

# --- Konfirmasi Hapus ---
if "konfirmasi_hapus_nik" in st.session_state:
    nik_target = st.session_state.konfirmasi_hapus_nik
    df_anggota = ambil_data(get_worksheet(sheet_url, "Anggota"))
    try:
        nama_target = df_anggota[df_anggota["nik"] == nik_target].iloc[0]["nama"]
    except:
        nama_target = "Tidak ditemukan"

    with st.expander("⚠️ Konfirmasi Penghapusan", expanded=True):
        st.error(f"Yakin ingin menghapus anggota **{nama_target}** (NIK: {nik_target})?")
        col_konf1, col_konf2 = st.columns(2)
        with col_konf1:
            if st.button("✅ Ya, Hapus Sekarang"):
                if hapus_berdasarkan_nik(nik_target):
                    st.success("✅ Data berhasil dihapus.")
                else:
                    st.error("❌ Gagal menghapus data.")
                del st.session_state.konfirmasi_hapus_nik
                st.rerun()
        with col_konf2:
            if st.button("❌ Batal"):
                del st.session_state.konfirmasi_hapus_nik
                st.rerun()
