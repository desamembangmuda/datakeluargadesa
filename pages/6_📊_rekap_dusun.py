import streamlit as st
import pandas as pd
from sheet_utils import get_worksheet
# Hapus baris ini sama sekali karena fungsinya sudah di file ini
# atau jika di file lain mau pakai fungsinya, gunakan:
# from sheet_utils import get_worksheet


st.set_page_config(page_title="Rekap per Dusun", layout="wide")

st.title("📊 Rekap Data per Dusun")

# --- Ambil data dari worksheet 'Anggota' ---
sheet_url = "https://docs.google.com/spreadsheets/d/1OjCLeZmypzFvThwmKF2PjheHU2NKedQbw9qzt8joKvs/edit?gid=675368762"
worksheet_name = "Anggota"

worksheet = get_worksheet(worksheet_name)

if worksheet:
    try:
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)

        # Validasi kolom 'dusun'
        if "dusun" not in df.columns:
            st.error("Kolom 'dusun' tidak ditemukan di worksheet 'Anggota'.")
        else:
            pilihan_dusun = st.selectbox("Pilih Dusun", options=["ALL", "dusun 1", "dusun 2", "dusun 3", "dusun 4", "dusun 5"])

            if pilihan_dusun == "ALL":
                st.subheader("📋 Seluruh Data Anggota")
                st.dataframe(df)
                st.success(f"Jumlah total anggota: {len(df)}")
            else:
                filtered_df = df[df["dusun"] == pilihan_dusun]
                st.subheader(f"📋 Data Anggota - {pilihan_dusun}")
                st.dataframe(filtered_df)
                st.success(f"Jumlah anggota di {pilihan_dusun}: {len(filtered_df)}")

    except Exception as e:
        st.error(f"❌ Gagal memuat data: {e}")
else:
    st.error("❌ Gagal mengakses worksheet 'Anggota'")
