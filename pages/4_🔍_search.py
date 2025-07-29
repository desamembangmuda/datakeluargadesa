import streamlit as st
if "login" not in st.session_state or not st.session_state["login"]:
    st.warning("⚠️ Silakan login terlebih dahulu.")
    st.stop()

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 🔐 Google Sheets Setup
def get_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["GOOGLE_SERVICE_ACCOUNT"], scope)
    client = gspread.authorize(creds)
    return client.open_by_key("1OjCLeZmypzFvThwmKF2PjheHU2NKedQbw9qzt8joKvs").worksheet(sheet_name)

def ambil_data_anggota():
    sheet = get_sheet("Anggota")
    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=[col.lower().strip() for col in data[0]])
    df['no kk'] = df['no kk'].str.strip()
    return df

def ambil_data_keluarga():
    sheet = get_sheet("Keluarga")
    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=[col.lower().strip() for col in data[0]])
    df['no kk'] = df['no kk'].str.strip()
    return df

def hapus_berdasarkan_nik(nik):
    sheet = get_sheet("Anggota")
    col_nik = sheet.col_values(5)
    for idx, val in enumerate(col_nik):
        if val.strip() == nik:
            sheet.delete_rows(idx + 1)
            return True
    return False

# 🌐 UI
st.set_page_config(page_title="Cari Anggota", layout="centered")
st.title("🔍 Cari Anggota Berdasarkan Nomor KK")

with st.form("form_search"):
    no_kk_input = st.text_input("Masukkan Nomor KK", max_chars=16)
    cari = st.form_submit_button("🔎 Cari")

if no_kk_input:
    try:
        df_anggota = ambil_data_anggota()
        df_keluarga = ambil_data_keluarga()

        no_kk_input = no_kk_input.strip()
        hasil_anggota = df_anggota[df_anggota['no kk'] == no_kk_input]
        hasil_keluarga = df_keluarga[df_keluarga['no kk'] == no_kk_input]
        nama_kk = hasil_keluarga.iloc[0]['nama kepala keluarga'] if not hasil_keluarga.empty else ""

        if not hasil_anggota.empty:
            st.subheader("📋 Tabel Anggota")

            for i, row in hasil_anggota.iterrows():
                with st.container():
                    cols = st.columns([3, 1, 1, 1])
                    with cols[0]:
                        st.write(f"**{row['nama']}** — NIK: `{row['nik']}` — {row['shdk']}")

                    with cols[1]:
                        if st.button("✏️ Edit", key=f"edit_{row['nik']}"):
                            st.session_state.no_kk = row['no kk']
                            st.session_state.nama_kk = nama_kk
                            st.session_state.edit_mode = True

                            # Simpan semua data ke session_state
                            st.session_state.edit_no_urut = row.get("no_urut", "")
                            st.session_state.edit_nama = row.get("nama", "")
                            st.session_state.edit_nik = row.get("nik", "")
                            st.session_state.edit_keberadaan = row.get("keberadaan", "Domisili Sesuai KK")
                            st.session_state.edit_jk = row.get("jenis kelamin", "Laki-laki")
                            st.session_state.edit_ijazah = row.get("ijazah", "Tidak tamat SD")
                            st.session_state.edit_status = row.get("status perkawinan", "Belum Kawin")
                            st.session_state.edit_shdk = row.get("shdk", "Kepala Rumah Tangga")
                            st.session_state.edit_status_pekerjaan = row.get("status pekerjaan", "Tidak Bekerja")
                            st.session_state.edit_pekerjaan = row.get("pekerjaan utama", "")
                            st.session_state.edit_lapangan = row.get("lapangan usaha", "Pertanian/Pekebunan/Peternakan")
                            st.session_state.edit_catatan = row.get("catatan", "")

                            try:
                                tgl = datetime.strptime(row['tanggal lahir'], "%m/%d/%Y").date()
                            except:
                                try:
                                    tgl = datetime.strptime(row['tanggal lahir'], "%d/%m/%Y").date()
                                except:
                                    tgl = datetime.today().date()
                            st.session_state.edit_tgl = tgl

                            # Debug opsional
                            # st.write("🔍 Semua key dalam row:", list(row.keys()))
                            # st.write("📦 Data row:", row.to_dict())

                            st.switch_page("pages/3_👨‍👩‍👧‍👦_form_anggota.py")

                    with cols[2]:
                        if st.button("🗑️ Hapus", key=f"hapus_{row['nik']}"):
                            st.session_state.konfirmasi_hapus_nik = row['nik']
                            st.rerun()

                    with cols[3]:
                        if st.button("➕ Tambah", key=f"add_{row['nik']}"):
                            st.session_state.no_kk = no_kk_input
                            st.session_state.nama_kk = nama_kk
                            st.session_state.edit_mode = False
                            for k in list(st.session_state.keys()):
                                if k.startswith("edit_"):
                                    del st.session_state[k]
                            st.switch_page("pages/3_👨‍👩‍👧‍👦_form_anggota.py")

        else:
            st.warning("❗ Nomor KK valid tapi belum memiliki data anggota.")
            if st.button("➕ Tambah Anggota"):
                st.session_state.no_kk = no_kk_input
                st.session_state.nama_kk = nama_kk
                st.session_state.edit_mode = False
                for k in list(st.session_state.keys()):
                    if k.startswith("edit_"):
                        del st.session_state[k]
                st.switch_page("pages/3_👨‍👩‍👧‍👦_form_anggota.py")

    except Exception as e:
        st.error(f"❌ Gagal memuat data: {e}")

# 🗑️ Konfirmasi Hapus
if "konfirmasi_hapus_nik" in st.session_state:
    nik_target = st.session_state.konfirmasi_hapus_nik
    df_anggota = ambil_data_anggota()
    nama_target = df_anggota[df_anggota['nik'] == nik_target].iloc[0]['nama']
    with st.expander("⚠️ Konfirmasi Hapus", expanded=True):
        st.error(f"Apakah kamu yakin ingin menghapus anggota **{nama_target}** (NIK: `{nik_target}`)?")
        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("✅ Ya, Hapus"):
                if hapus_berdasarkan_nik(nik_target):
                    st.success("Data berhasil dihapus.")
                else:
                    st.error("Gagal menghapus data.")
                del st.session_state.konfirmasi_hapus_nik
                st.rerun()
        with col_b:
            if st.button("❌ Batal"):
                del st.session_state.konfirmasi_hapus_nik
                st.rerun()
