import streamlit as st
import pandas as pd

st.header("👥 Form Anggota Keluarga")

jumlah = st.number_input("Jumlah Anggota", min_value=1, max_value=10, value=1)

data = []
for i in range(int(jumlah)):
    st.markdown(f"### Anggota #{i+1}")
    nama = st.text_input(f"Nama", key=f"nama{i}")
    nik = st.text_input(f"NIK", key=f"nik{i}")
    umur = st.number_input(f"Umur", min_value=0, max_value=120, key=f"umur{i}")
    jk = st.selectbox(f"Jenis Kelamin", ["Laki-laki", "Perempuan"], key=f"jk{i}")
    shdk = st.selectbox(f"SHDK", ["Anak", "Istri", "Kepala Keluarga", "Lainnya"], key=f"shdk{i}")
    data.append({
        "Nama": nama, "NIK": nik, "Umur": umur, "Jenis Kelamin": jk, "SHDK": shdk
    })

if st.button("Simpan Anggota"):
    df = pd.DataFrame(data)
    st.dataframe(df)
