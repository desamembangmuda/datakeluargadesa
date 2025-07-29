import streamlit as st
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ========= CEK LOGIN =========
if "login" not in st.session_state or not st.session_state["login"]:
    st.warning("⚠️ Silakan login terlebih dahulu.")
    st.stop()

# ========= KONEKSI SHEETS =========
def connect_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["GOOGLE_SERVICE_ACCOUNT"], scope)
    client = gspread.authorize(creds)
    return client.open_by_key("1OjCLeZmypzFvThwmKF2PjheHU2NKedQbw9qzt8joKvs").worksheet("Keluarga")
    return sheet
   
def is_no_kk_duplicate(no_kk):
    sheet = connect_sheet()
    existing_data = [str(cell).strip() for cell in sheet.col_values(2)]
    return str(no_kk).strip() in existing_data

def simpan_ke_sheets(data):
    sheet = connect_sheet()
    sheet.append_row(data, value_input_option="USER_ENTERED")

# ========= FORM INPUT =========
st.set_page_config(page_title="Form Keluarga", layout="centered")
st.title("📝 Form Pendataan Kepala Keluarga")

with st.form("form_keluarga"):
    st.subheader("Wilayah")
    st.text_input("Provinsi", value="Sumatera Utara", disabled=True)
    st.text_input("Kabupaten", value="Labuhanbatu Utara", disabled=True)
    st.text_input("Kecamatan", value="Kualuh Hulu", disabled=True)
    st.text_input("Desa", value="MambangMuda", disabled=True)
    dusun = st.selectbox("Dusun", ["DUSUN 1", "DUSUN 2", "DUSUN 3", "DUSUN 4", "Dusun 5"])
    alamat = st.text_area("Alamat")

    st.subheader("Keterangan Petugas")
    nama_petugas = st.text_input("Nama Petugas Pendataan",value="NONAME", disabled=True)
    nama_pengawas = st.text_input("Nama Petugas Pengawas",value="NONAME", disabled=True)
    tanggal_input = st.date_input("Tanggal Pendataan", disabled=True)

    st.subheader("Data Keluarga")
    no_kk = st.text_input("No KK", max_chars=16)
    nama_kepala = st.text_input("Nama Kepala Keluarga")
    jumlah_anggota = st.number_input("Jumlah Anggota Keluarga", min_value=1, step=1)

    st.markdown("Bantuan yang Diterima")
    bantuan_pkh = st.checkbox("PKH")
    bantuan_bpnt = st.checkbox("BPNT")
    bantuan_blt = st.checkbox("BLT")
    bantuan_lain = st.text_input("Lainnya (contoh: BSU)")

    submit = st.form_submit_button("💾 Simpan & Lanjut")

# ========= PROSES SETELAH DISUBMIT =========
if submit:
    # Validasi dasar
    if not all([no_kk, nama_kepala, dusun, alamat, nama_petugas, nama_pengawas]):
        st.warning("⚠️ Semua kolom wajib diisi.")
    elif not no_kk.isdigit() or len(no_kk) != 16:
        st.error("❌ No KK harus terdiri dari 16 digit angka.")
    elif is_no_kk_duplicate(no_kk):
        st.error("❌ No KK sudah ada dalam database.")
    else:
        # Simpan bantuan
        bantuan_list = []
        if bantuan_pkh: bantuan_list.append("PKH")
        if bantuan_bpnt: bantuan_list.append("BPNT")
        if bantuan_blt: bantuan_list.append("BLT")
        if bantuan_lain: bantuan_list.append(bantuan_lain)
        bantuan = ", ".join(bantuan_list) if bantuan_list else "-"

        # Simpan ke Google Sheets
        try:
            simpan_ke_sheets([
                no_kk,
                nama_kepala,
                dusun,
                alamat,
                nama_petugas,
                nama_pengawas,
                tanggal_input.strftime('%d/%m/%Y'),
                int(jumlah_anggota),
                bantuan
            ])

            # Set session_state
            st.session_state.no_kk = no_kk
            st.session_state.jumlah_anggota = int(jumlah_anggota)

            st.success("✅ Data keluarga berhasil disimpan!")
            st.switch_page("pages/3_👨‍👩‍👧‍👦_form_anggota.py")

        except Exception as e:
            st.error(f"❌ Gagal menyimpan: {e}")
