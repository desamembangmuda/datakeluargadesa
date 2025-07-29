import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

# 🔑 Inisialisasi client dan koneksi ke Google Sheet
def get_worksheet(worksheet_name: str):
    """
    Mengembalikan worksheet dari Google Spreadsheet berdasarkan nama sheet.
    Worksheet URL diambil dari st.secrets["sheet_url"]
    """
    try:
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["GOOGLE_SERVICE_ACCOUNT"], scope)
        client = gspread.authorize(creds)

        sheet_url = st.secrets["sheet_url"]
        sheet = client.open_by_url(sheet_url)
        worksheet = sheet.worksheet(worksheet_name)

        return worksheet

    except gspread.exceptions.WorksheetNotFound:
        st.error(f"❌ Worksheet '{worksheet_name}' tidak ditemukan di spreadsheet.")
    except KeyError:
        st.error("❌ Pastikan 'sheet_url' tersedia di secrets.toml.")
    except Exception as e:
        st.error(f"❌ Gagal membuka worksheet: {e}")

    return None


# 📌 Fungsi untuk menentukan posisi penyisipan berdasarkan SHDK
def cari_index_penyisipan(sheet, no_kk: str, shdk: str) -> int:
    """
    Menentukan posisi baris untuk menyisipkan data anggota baru berdasarkan SHDK.
    """
    data = sheet.get_all_records()

    kepala_row = None
    istri_row = None
    last_anak_row = None
    last_row_kk = None

    for idx, row in enumerate(data):
        row_num = idx + 2  # +2 karena header di baris 1, data mulai baris 2
        if str(row.get("no kk", "")).strip() == no_kk.strip():
            last_row_kk = row_num
            shdk_l = str(row.get("shdk", "")).strip().lower()
            if shdk_l == "kepala rumah tangga":
                kepala_row = row_num
            elif shdk_l in ["suami", "istri", "suami/istri"]:
                istri_row = row_num
            elif shdk_l == "anak":
                last_anak_row = row_num

    shdk = shdk.strip().lower()

    if shdk == "kepala rumah tangga" or kepala_row is None:
        return len(data) + 2  # tambah di akhir jika belum ada kepala

    if shdk in ["suami", "istri", "suami/istri"]:
        return kepala_row + 1

    if shdk == "anak":
        if last_anak_row:
            return last_anak_row + 1
        elif istri_row:
            return istri_row + 1
        else:
            return kepala_row + 1

    # Untuk anggota lain seperti cucu, mertua, dll
    if last_anak_row:
        return last_anak_row + 1
    elif istri_row:
        return istri_row + 1
    else:
        return kepala_row + 1


# 📊 Fungsi untuk mengurutkan dan memperbarui no_urut
def urutkan_dan_perbarui_no_urut(sheet):
    """
    Mengurutkan seluruh data berdasarkan No KK, SHDK, dan umur tertua ke muda,
    lalu memperbarui kolom 'no_urut' agar urut dimulai dari 1 per KK.
    """
    data = sheet.get_all_values()
    if len(data) < 2:
        return  # Kosong atau hanya header

    header = data[0]
    records = data[1:]

    try:
        idx_kk = header.index("no kk")
        idx_shdk = header.index("shdk")
        idx_umur = header.index("umur")
        idx_no_urut = header.index("no_urut")

        def bobot_shdk(shdk):
            urutan = {
                "kepala rumah tangga": 0,
                "suami/istri": 1,
                "suami": 1,
                "istri": 1,
                "anak": 2
            }
            return urutan.get(shdk.strip().lower(), 3)

        # Sort data
        records.sort(key=lambda row: (
            row[idx_kk],
            bobot_shdk(row[idx_shdk]),
            -int(row[idx_umur]) if row[idx_umur].isdigit() else 0
        ))

        # Perbarui no_urut per KK
        no_urut_per_kk = {}
        for row in records:
            kk = row[idx_kk]
            no_urut_per_kk.setdefault(kk, 0)
            no_urut_per_kk[kk] += 1
            row[idx_no_urut] = str(no_urut_per_kk[kk])

        # Tulis ulang ke sheet
        sheet.clear()
        sheet.append_row(header)
        for row in records:
            sheet.append_row(row)

    except Exception as e:
        st.error(f"❌ Gagal mengurutkan data: {e}")
