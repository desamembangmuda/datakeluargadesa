import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard Visualisasi", layout="wide")
st.title("📊 Dashboard Visualisasi Pendataan Desa MembangMuda")

# Cek login
if "login" not in st.session_state or not st.session_state["login"]:
    st.warning("⚠️ Silakan login terlebih dahulu.")
    st.stop()

# Fungsi koneksi ke Google Sheets
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["GOOGLE_SERVICE_ACCOUNT"], scope)
    client = gspread.authorize(creds)
    return client.open_by_key("1OjCLeZmypzFvThwmKF2PjheHU2NKedQbw9qzt8joKvs").worksheet("Anggota")

# Ambil data
def ambil_data():
    sheet = get_sheet()
    records = sheet.get_all_values()
    df = pd.DataFrame(records[1:], columns=[col.lower().strip() for col in records[0]])
    return df

try:
    df = ambil_data()

    if df.empty:
        st.info("Belum ada data untuk divisualisasikan.")
        st.stop()

    # Bersihkan string & hilangkan baris dengan data penting kosong
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    kolom_penting = ["jenis kelamin", "ijazah", "status pekerjaan", "kelompok umur"]
    df = df.dropna(subset=kolom_penting)
    for kolom in kolom_penting:
        df = df[df[kolom].astype(str).str.strip() != ""]

    # Format teks
    df['dusun'] = df['dusun'].str.title().str.strip()
    df['jenis kelamin'] = df['jenis kelamin'].str.title()
    df['ijazah'] = df['ijazah'].str.upper()
    df['status pekerjaan'] = df['status pekerjaan'].str.title()
    df['kelompok umur'] = df['kelompok umur'].str.strip()

    # Filter dusun
    if 'dusun' in df.columns:
        semua_dusun = sorted(df['dusun'].dropna().unique().tolist())
        pilihan_dusun = ["All"] + semua_dusun
        dusun_dipilih = st.selectbox("📍 Filter Berdasarkan Dusun", pilihan_dusun)
        if dusun_dipilih != "All":
            df = df[df['dusun'] == dusun_dipilih]

    # Konversi umur
    df['umur'] = pd.to_numeric(df['umur'], errors='coerce').fillna(0).astype(int)

    # Urutan kelompok umur
    urutan_kelompok = ["0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39",
                       "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74",
                       "75-79", "80-84", "85-89"]
    df["kelompok umur"] = pd.Categorical(df["kelompok umur"], categories=urutan_kelompok, ordered=True)

    # Layout atas
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Jenis Kelamin")
        fig1 = px.pie(df, names="jenis kelamin", hole=0.4)
        color_discrete_sequence=["orange", "blue"]
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Ijazah Tertinggi")
        pendidikan_count = df["ijazah"].value_counts().reset_index()
        pendidikan_count.columns = ["ijazah", "jumlah"]
        fig2 = px.bar(pendidikan_count, x="ijazah", y="jumlah",)
        color_discrete_sequence=["blue"]
        st.plotly_chart(fig2, use_container_width=True)

    # Layout bawah
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Status Pekerjaan")
        status_pekerjaan_count = df["status pekerjaan"].value_counts().reset_index()
        status_pekerjaan_count.columns = ["status", "jumlah"]
        fig4 = px.bar(status_pekerjaan_count, x="status", y="jumlah",)
        color_discrete_sequence=["green"]
        st.plotly_chart(fig4, use_container_width=True)

    with col4:
        st.subheader("Piramida Penduduk Berdasarkan Kelompok Umur & Jenis Kelamin")
        piramida_df = df.groupby(["kelompok umur", "jenis kelamin"]).size().unstack(fill_value=0).reindex(urutan_kelompok)
        piramida_df = piramida_df.fillna(0)

        # Jika hanya 1 gender tersedia, tambahkan kolom kosong agar tetap bisa diplot
        if 'Laki - Laki' not in piramida_df.columns:
            piramida_df['Laki - Laki'] = 0
        if 'Perempuan' not in piramida_df.columns:
            piramida_df['Perempuan'] = 0

        piramida_df['Laki - Laki'] = -piramida_df['Laki - Laki']  # agar ke kiri

        fig5 = px.bar(
            piramida_df.reset_index().melt(id_vars='kelompok umur', value_name='jumlah'),
            x="jumlah", y="kelompok umur", color="jenis kelamin", orientation="h",
            color_discrete_map={"Laki - Laki": "blue", "Perempuan": "orange"},
            labels={"jumlah": "Jumlah", "kelompok umur": "Kelompok Umur", "jenis kelamin": "Jenis Kelamin"},
            title="Piramida Penduduk"
        )
        fig5.update_layout(bargap=0.1)
        st.plotly_chart(fig5, use_container_width=True)

except Exception as e:
    st.error(f"❌ Gagal memuat dashboard: {e}")
