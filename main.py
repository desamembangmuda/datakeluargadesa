import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def simpan_ke_sheets(data: pd.DataFrame, sheet_name: str = "DataKeluarga", worksheet_index: int = 0):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name)
    worksheet = sheet.get_worksheet(worksheet_index)
    rows = data.values.tolist()
    for row in rows:
        worksheet.append_row(row)


st.set_page_config(page_title="Aplikasi Data Keluarga", layout="wide")
st.title("📊 Aplikasi Entri Data Keluarga")

st.write("""
Selamat datang di Aplikasi Pendataan Keluarga berbasis Web.

Gunakan menu di sebelah kiri untuk mengakses:
- 📋 Form Data Kepala Keluarga
- 👥 Form Data Anggota Keluarga
""")
