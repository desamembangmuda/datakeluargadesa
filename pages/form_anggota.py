import streamlit as st
import pandas as pd
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ===== Fungsi Simpan ke Google Sheets =====
def simpan_ke_sheets(dataframe):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)

    spreadsheet_id = "1LOv15OJL__vKiok8qmJqPGt4Je4nmxVSV0_a0ed8L5w"
    sheet = client.open_by_key(spreadsheet_id).worksheet("Anggota")  # worksheet: "Anggota"

    rows = dataframe.values.tolist()
    sheet.append_rows(rows, value_input_option="USER_ENTERED")

# ===== UI Form Anggota =====
st.set_page_config(page_title="Form Anggota Keluarga", layout="centered")
st.title("👥 Form Anggota Keluarga")

# Validasi session state dari form keluarga
if "no_kk" not in st.session_state or "nama_kk" not in st.session_state:
    st.warning("⚠️ Silakan isi Form Keluarga terlebih dahulu.")
    st.stop()

# Tampilkan identitas keluarga
st.info(f"🆔 No KK: **{st.session_state.no_kk}**")
st.info(f"👤 Kepala Keluarga: **{st.session_state.nama_kk}**")
st.info(f"📌 Jumlah Anggota Keluarga: **{st.session_state.jumlah_anggota}**")

jumlah = int(st.session_state.jumlah_anggota)
data = []

for i in range(jumlah):
    st.markdown(f"### 🧍 Anggota #{i+1}")
    nama = st.text_input("Nama", key=f"nama{i}")

    nik = st.text_input("NIK (16 digit)", max_chars=16, key=f"nik{i}")
    if nik and (not nik.isdigit() or len(nik) != 16):
        st.warning(f"❗ NIK anggota #{i+1} harus 16 digit angka.")

    tanggal_lahir = st.date_input(
        "Tanggal Lahir",
        value=date(2000, 1, 1),
        min_value=date(1945, 1, 1),
        max_value=date.today(),
        key=f"tgl{i}"
    )

    umur = date.today().year - tanggal_lahir.year - (
        (date.today().month, date.today().day) < (tanggal_lahir.month, tanggal_lahir.day)
    )

    st.button(f"🎂 Umur: {umur} tahun", key=f"umur_button{i}", disabled=True)

    keberadaan = st.selectbox("Keberadaan", ["Domisili Sesuai KK", "Tidak Sesuai KK", "Meninggal", "Lainnya"], key=f"keberadaan{i}")
    jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"], key=f"jk{i}")
    ijazah = st.selectbox("Ijazah Tertinggi", ["SD", "SMP", "SMA", "Perguruan Tinggi"], key=f"ijazah{i}")
    status = st.selectbox("Status Perkawinan", ["Belum Kawin", "Kawin", "Cerai Hidup", "Cerai Mati"], key=f"status{i}")
    status_pekerjaan = st.selectbox("Status Pekerjaan", ["Tidak Bekerja", "Berusaha Sendiri", "Buruh/Karyawan", "Pegawai"], key=f"status_pekerjaan{i}")
    pekerjaan = st.text_input("Pekerjaan Utama", key=f"pekerjaan{i}")
    lapangan = st.selectbox("Lapangan Usaha", [
        "Pertanian", "Industri", "Konstruksi", "Perdagangan", "Penyedian makanan/minum",
        "Administrsi", "Pemerintahan", "Pendidikan", "Kesehatan", "Lainnya"
    ], key=f"lapangan{i}")
    shdk = st.selectbox("SHDK", ["Kepala Keluarga", "Istri", "Anak", "Cucu", "Orang tua/Mertua", "Family Lainnya"], key=f"shdk{i}")

    data.append([
        st.session_state.no_kk,
        st.session_state.nama_kk,
        nama,
        nik,
        keberadaan,
        tanggal_lahir.strftime('%d/%m/%Y'),
        umur,
        jk,
        ijazah,
        status,
        status_pekerjaan,
        pekerjaan,
        lapangan,
        shdk
    ])

# ===== Simpan ke Google Sheets saat submit =====
if st.button("✅ Simpan Anggota"):
    df = pd.DataFrame(data, columns=[
        "No KK", "Nama KK", "Nama", "NIK", "Keberadaan", "Tanggal Lahir", "Umur",
        "Jenis Kelamin", "Ijazah", "Status Perkawinan", "Status Pekerjaan", "Pekerjaan Utama", "Lapangan Usaha", "SHDK"
    ])
    try:
        simpan_ke_sheets(df)
        st.success("✅ Data anggota keluarga berhasil disimpan ke Google Sheets!")
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Gagal menyimpan ke Google Sheets: {e}")
