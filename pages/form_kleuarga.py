import streamlit as st

st.header("📋 Form Kepala Keluarga")

no_kk = st.text_input("Nomor KK")
nama_kk = st.text_input("Nama Kepala Keluarga")
alamat = st.text_area("Alamat")

if st.button("Simpan Kepala Keluarga"):
    st.success(f"✅ Data {nama_kk} berhasil disimpan.")
