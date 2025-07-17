import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px

# Cek login
if "login" not in st.session_state or not st.session_state["login"]:
    st.warning("⚠️ Silakan login terlebih dahulu.")
    st.stop()

# Fungsi koneksi ke Google Sheets
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)
    return client.open_by_key("1OjCLeZmypzFvThwmKF2PjheHU2NKedQbw9qzt8joKvs").worksheet("Anggota")
    
# Ambil data
def ambil_data():
    sheet = get_sheet()
    records = sheet.get_all_values()
    df = pd.DataFrame(records[1:], columns=[col.lower().strip() for col in records[0]])
    return df

# Judul
st.set_page_config(page_title="Dashboard Visualisasi", layout="wide")
st.title("📊 Dashboard Visualisasi Pendataan Desa MembangMuda")

try:
    df = ambil_data()

    if df.empty:
        st.info("Belum ada data untuk divisualisasikan.")
        st.stop()

    # ✅ Filter Dusun
    if 'dusun' in df.columns:
        df['dusun'] = df['dusun'].str.title().str.strip()  # Kapitalisasi dan hilangkan spasi
        semua_dusun = sorted(df['dusun'].dropna().unique().tolist())
        pilihan_dusun = ["All"] + semua_dusun
        dusun_dipilih = st.selectbox("📍 Filter Berdasarkan Dusun", pilihan_dusun)

        if dusun_dipilih != "All":
            df = df[df['dusun'] == dusun_dipilih]

    # Konversi umur ke int
    df['umur'] = pd.to_numeric(df['umur'], errors='coerce').fillna(0).astype(int)

    # Tambah kelompok umur
    def kelompok_umur(u):
        if u <= 5: return "Balita"
        elif u <= 12: return "Anak"
        elif u <= 17: return "Remaja"
        elif u <= 59: return "Dewasa"
        else: return "Lansia"

    df["kelompok_umur"] = df["umur"].apply(kelompok_umur)

    # Baris atas
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Jenis Kelamin")
        fig1 = px.pie(df, names="jenis kelamin", title="Distribusi Jenis Kelamin", hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Ijazah Tertinggi")
        pendidikan_count = df["ijazah"].value_counts().reset_index()
        pendidikan_count.columns = ["ijazah", "jumlah"]
        fig2 = px.bar(pendidikan_count,
                      x="ijazah", y="jumlah",
                      title="Distribusi Pendidikan")
        st.plotly_chart(fig2, use_container_width=True)

    # Baris bawah
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Kelompok Umur")
        fig3 = px.pie(df, names="kelompok_umur", title="Kelompok Umur", hole=0.4)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Status Pekerjaan")
        status_pekerjaan_count = df["status pekerjaan"].value_counts().reset_index()
        status_pekerjaan_count.columns = ["status", "jumlah"]
        fig4 = px.bar(status_pekerjaan_count,
                      x="status", y="jumlah",
                      title="Distribusi Status Bekerja")
        st.plotly_chart(fig4, use_container_width=True)

except Exception as e:
    st.error(f"❌ Gagal memuat dashboard: {e}")
