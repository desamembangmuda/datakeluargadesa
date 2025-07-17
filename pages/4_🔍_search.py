import streamlit as st
import gspread
import pandas as pd
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# ✅ Verifikasi Login
if "login" not in st.session_state or not st.session_state["login"]:
    st.warning("⚠️ Silakan login terlebih dahulu.")
    st.stop()

try:
    st.write("🔐 client_email:", st.secrets["GOOGLE_SERVICE_ACCOUNT"]["client_email"])
except Exception as e:
    st.error("❌ Tidak bisa akses secret `GOOGLE_SERVICE_ACCOUNT`.")
    st.code(str(e))
    st.stop()

# Setup koneksi Google Sheets
def get_worksheet(sheet_url, worksheet_name):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["GOOGLE_SERVICE_ACCOUNT"], scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_url(sheet_url)
        worksheet = spreadsheet.worksheet(worksheet_name)
        return worksheet
    except Exception as e:
        st.error(f"❌ Gagal mengakses Google Sheet: {worksheet_name}")
        st.code(str(e))
        return None

# Ganti sesuai URL & worksheet
sheet_url = "https://docs.google.com/spreadsheets/d/1OjCLeZmypzFvThwmKF2PjheHU2NKedQbw9qzt8joKvs/edit?gid=0#gid=0"

# Tampilkan Data Keluarga
st.subheader("👨‍👩‍👧‍👦 Tabel Data Keluarga")
worksheet_keluarga = get_worksheet(sheet_url, "data_keluarga")
if worksheet_keluarga:
    try:
        data_keluarga = worksheet_keluarga.get_all_records()
        df_keluarga = pd.DataFrame(data_keluarga)
        st.dataframe(df_keluarga)
    except Exception as e:
        st.error("❌ Gagal memuat data: data_keluarga")
        st.code(str(e))

# Tampilkan Data Anggota
st.subheader("🧍‍♂️ Tabel Anggota Keluarga")
worksheet_anggota = get_worksheet(sheet_url, "Anggota")
if worksheet_anggota:
    try:
        data_anggota = worksheet_anggota.get_all_records()
        df_anggota = pd.DataFrame(data_anggota)
        st.dataframe(df_anggota)
    except Exception as e:
        st.error("❌ Gagal memuat data: Anggota")
        st.code(str(e))

def ambil_data(sheet_name):
    try:
        sheet = get_sheet(sheet_name)
        data = sheet.get_all_values()
        if len(data) < 2:
            return pd.DataFrame()  # Kosong
        df = pd.DataFrame(data[1:], columns=[col.lower().strip() for col in data[0]])
        if 'no kk' not in df.columns:
            raise ValueError(f"Kolom 'no kk' tidak ditemukan di sheet '{sheet_name}'")
        df['no kk'] = df['no kk'].str.strip()
        return df
    except Exception as e:
        st.error(f"❌ Gagal memuat data dari sheet '{sheet_name}'")
        st.code(str(e))
        return pd.DataFrame()

def ambil_data_anggota():
    return ambil_data("Anggota")

def ambil_data_keluarga():
    return ambil_data("Keluarga")

def hapus_berdasarkan_nik(nik):
    try:
        sheet = get_sheet("Anggota")
        col_nik = sheet.col_values(5)
        for idx, val in enumerate(col_nik):
            if val.strip() == nik:
                sheet.delete_rows(idx + 1)
                return True
    except Exception as e:
        st.error("❌ Gagal menghapus data.")
        st.code(str(e))
    return False

# 🌐 UI
st.set_page_config(page_title="Cari Anggota", layout="centered")
st.title("🔍 Cari Anggota Berdasarkan Nomor KK")

with st.form("form_search"):
    no_kk_input = st.text_input("Masukkan Nomor KK", max_chars=16)
    cari = st.form_submit_button("🔎 Cari")

if no_kk_input:
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
                    st.write(f"**{row['nama']}** — NIK: {row['nik']} — {row['shdk']}")

                with cols[1]:
                    if st.button("✏️ Edit", key=f"edit_{row['nik']}"):
                        st.session_state.no_kk = row['no kk']
                        st.session_state.nama_kk = nama_kk
                        st.session_state.edit_mode = True

                        # Simpan data ke session
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

                        st.switch_page("pages/2_👪_form_anggota.py")

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
                        st.switch_page("pages/2_👪_form_anggota.py")
    else:
        st.warning("❗ Nomor KK valid tapi belum memiliki data anggota.")
        if st.button("➕ Tambah Anggota"):
            st.session_state.no_kk = no_kk_input
            st.session_state.nama_kk = nama_kk
            st.session_state.edit_mode = False
            for k in list(st.session_state.keys()):
                if k.startswith("edit_"):
                    del st.session_state[k]
            st.switch_page("pages/2_👪_form_anggota.py")

# 🗑️ Konfirmasi Hapus
if "konfirmasi_hapus_nik" in st.session_state:
    nik_target = st.session_state.konfirmasi_hapus_nik
    df_anggota = ambil_data_anggota()
    try:
        nama_target = df_anggota[df_anggota['nik'] == nik_target].iloc[0]['nama']
    except:
        nama_target = "Tidak ditemukan"

    with st.expander("⚠️ Konfirmasi Hapus", expanded=True):
        st.error(f"Apakah kamu yakin ingin menghapus anggota **{nama_target}** (NIK: {nik_target})?")
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
