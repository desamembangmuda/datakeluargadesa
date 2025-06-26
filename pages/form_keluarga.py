import streamlit as st
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ======== FUNGSI SIMPAN KE GOOGLE SHEETS =========
def simpan_ke_sheets(data):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)

    spreadsheet_id = "1LOv15OJL__vKiok8qmJqPGt4Je4nmxVSV0_a0ed8L5w"
    sheet = client.open_by_key(spreadsheet_id).worksheet("Keluarga")  # worksheet 'Keluarga'
    sheet.append_row(data, value_input_option="USER_ENTERED")

# ========== UI FORM ============
st.set_page_config(page_title="Form Pendataan Kepala Keluarga", layout="centered")
st.title("📝 Form Pendataan Kepala Keluarga")

with st.form("form_kepala_keluarga", clear_on_submit=True):
    st.subheader("Wilayah")
    st.text_input("Provinsi", value="Sumatera Utara", disabled=True)
    st.text_input("Kabupaten", value="Labuhanbatu Utara", disabled=True)
    st.text_input("Kecamatan", value="Kualuh Hulu", disabled=True)
    st.text_input("Desa", value="MambangMuda", disabled=True)

    dusun = st.text_input("Dusun")
    alamat = st.text_area("Alamat")

    st.subheader("Keterangan Petugas")
    nama_petugas = st.text_input("Nama Petugas Pendataan")
    nama_petugas1 = st.text_input("Nama Petugas Pengawas")
    tanggal_input = st.date_input("Tanggal Pendataan", value=date.today())

    st.subheader("Data Keluarga")
    noKK = st.text_input("No KK", max_chars=16)
    nama_KepalaKeluarga = st.text_input("Nama Kepala Keluarga")
    jumlah_anggota = st.number_input("Jumlah Anggota Keluarga", min_value=1, step=1)

    simpan = st.form_submit_button("💾 Simpan & Lanjut")

# ========== LOGIKA PENYIMPANAN ============
if simpan:
    if not noKK.isdigit() or len(noKK) != 16:
        st.error("❌ No KK harus 16 digit angka.")
    else:
        # Simpan ke session_state
        st.session_state.no_kk = noKK
        st.session_state.nama_kk = nama_KepalaKeluarga
        st.session_state.jumlah_anggota = jumlah_anggota

        # Simpan ke spreadsheet
        data_keluarga = [
            noKK,
            nama_KepalaKeluarga,
            dusun,
            alamat,
            nama_petugas,
            nama_petugas1,
            str(tanggal_input),
            jumlah_anggota
        ]
        try:
            simpan_ke_sheets(data_keluarga)
            st.success("✅ Data keluarga berhasil disimpan ke Google Sheets.")
            st.switch_page("pages/form_anggota.py")
        except Exception as e:
            st.error(f"❌ Gagal menyimpan ke Google Sheets: {e}")
