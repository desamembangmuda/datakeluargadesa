import streamlit as st
from datetime import date, datetime
import uuid
from sheet_utils import get_worksheet, cari_index_penyisipan

# ============================
# 🔧 Utility Functions
# ============================
def hitung_umur(tanggal_lahir: date) -> int:
    today = date.today()
    umur = today.year - tanggal_lahir.year - ((today.month, today.day) < (tanggal_lahir.month, tanggal_lahir.day))
    return umur


def generate_id():
    return uuid.uuid4().hex[:8]

def parse_tanggal_lahir(tgl_str):
    if isinstance(tgl_str, date):
        return tgl_str
    for fmt in ('%d/%m/%Y', '%m/%d/%Y'):
        try:
            return datetime.strptime(tgl_str, fmt).date()
        except:
            continue
    return date.today()

def normalize(value, options, default):
    value = str(value).strip().replace(" - ", "-").capitalize()
    for opt in options:
        if value.lower() == opt.lower():
            return opt
    return default

def cek_nik_ganda(sheet, nik_baru):
    existing_data = sheet.col_values(5)[1:]  # Skip header
    return nik_baru in [x.replace("'", "") for x in existing_data]

def simpan_ke_sheets(sheet, data, no_kk, shdk):
    posisi = cari_index_penyisipan(sheet, no_kk, shdk)
    sheet.insert_row(data, index=posisi, value_input_option="USER_ENTERED")

def update_berdasarkan_nik(sheet, nik_lama, data_baru):
    col = sheet.col_values(5)
    for idx, val in enumerate(col):
        if val.strip().replace("'", "") == nik_lama.strip().replace("'", ""):
            sheet.delete_rows(idx + 1)
            sheet.insert_row(data_baru, index=idx + 1, value_input_option="USER_ENTERED")
            return True
    return False

# ============================
# ✅ Validasi Login & KK
# ============================
if "login" not in st.session_state or not st.session_state["login"]:
    st.warning("⚠️ Silakan login terlebih dahulu.")
    st.stop()

if not st.session_state.get("no_kk", ""):
    st.warning("⚠️ Silakan isi data keluarga terlebih dahulu.")
    st.stop()

# ============================
# 📋 Konfigurasi awal
# ============================
st.set_page_config(page_title="Form Anggota Keluarga", layout="centered")
st.title("Form Anggota Keluarga")

st.session_state.setdefault("jumlah_anggota", 1)
st.session_state.setdefault("anggota_ke", 1)
st.session_state.setdefault("anggota_data", [])
st.session_state.setdefault("edit_mode", False)

st.subheader(f"Anggota Keluarga ke-{st.session_state.anggota_ke} dari {st.session_state.jumlah_anggota}")
st.text(f"Nomor KK: {st.session_state.no_kk}")

sheet = get_worksheet("Anggota")

# ============================
# 📝 Form Input
# ============================
with st.form("form_anggota", clear_on_submit=not st.session_state.edit_mode):
    no_urut = st.text_input("No Urut Anggota", value=st.session_state.get("edit_no_urut", ""))
    nama = st.text_input("Nama", value=st.session_state.get("edit_nama", ""))
    nik = st.text_input("NIK (16 digit, unik)", max_chars=16, value=st.session_state.get("edit_nik", ""))

    keberadaan_options = ["Domisili Sesuai KK", "Domisili Tidak Sesuai KK", "Meninggal", "Anggota Keluarga Baru"]
    keberadaan = st.selectbox("Keberadaan", keberadaan_options,
        index=keberadaan_options.index(normalize(st.session_state.get("edit_keberadaan", "Domisili Sesuai KK"), keberadaan_options, "Domisili Sesuai KK")))

    jk_options = ["Laki - Laki", "Perempuan"]
    jk = st.selectbox("Jenis Kelamin", jk_options,
        index=jk_options.index(normalize(st.session_state.get("edit_jk", "Laki - Laki"), jk_options, "Laki - Laki")))

    tanggal_default = parse_tanggal_lahir(st.session_state.get("edit_tgl", "01/01/2025"))
    tanggal_lahir = st.date_input("Tanggal Lahir", value=tanggal_default, min_value=date(1945, 1, 1), max_value=date.today())
    umur = hitung_umur(tanggal_lahir)
    st.success(f"Umur: {umur} tahun")

    ijazah_options = ["Tidak tamat SD", "SD", "SMP/MI", "SMA/SMK/MA", "D1/D2/D3", "S1/D4", "S2/S3"]
    ijazah = st.selectbox("Ijazah Tertinggi", ijazah_options,
        index=ijazah_options.index(normalize(st.session_state.get("edit_ijazah", "Tidak tamat SD"), ijazah_options, "Tidak tamat SD")))

    status_options = ["Belum Kawin", "Kawin/Nikah", "Cerai Hidup", "Cerai Mati"]
    status = st.selectbox("Status Perkawinan", status_options,
        index=status_options.index(normalize(st.session_state.get("edit_status", "Belum Kawin"), status_options, "Belum Kawin")))

    shdk_options = ["Kepala Rumah Tangga", "Suami/Istri", "Anak", "Cucu", "Orang tua/Mertua", "Family Lainnya"]
    shdk = st.selectbox("SHDK", shdk_options,
        index=shdk_options.index(normalize(st.session_state.get("edit_shdk", "Kepala Rumah Tangga"), shdk_options, "Kepala Rumah Tangga")))

    status_pekerjaan_options = ["Tidak Bekerja", "Berusaha Sendiri", "Buruh/Karyawan/Pegawai", "Pekerja Tidak Dibayar/Pekerja Keluarga"]
    status_pekerjaan = st.selectbox("Status Pekerjaan", status_pekerjaan_options,
        index=status_pekerjaan_options.index(normalize(st.session_state.get("edit_status_pekerjaan", "Tidak Bekerja"), status_pekerjaan_options, "Tidak Bekerja")))

    pekerjaan = st.text_input("Pekerjaan Utama", value=st.session_state.get("edit_pekerjaan", ""))

    lapangan_options = ["Pertanian/Pekebunan/Peternakan", "Industri", "Konstruksi", "Perdagangan", "Pemerintahan", "Pendidikan", "Penyediaan Makanan/Minuman", "Kesehatan", "Lainnya"]
    lapangan = st.selectbox("Lapangan Usaha", lapangan_options,
        index=lapangan_options.index(normalize(st.session_state.get("edit_lapangan", "Pertanian/Pekebunan/Peternakan"), lapangan_options, "Pertanian/Pekebunan/Peternakan")))

    catatan = st.text_input("Catatan", value=st.session_state.get("edit_catatan", ""))

    simpan = st.form_submit_button("💾 Simpan")

# ============================
# 💾 Proses Simpan
# ============================
if simpan:
    if not all([no_urut, nama, nik]):
        st.warning("⚠️ No Urut, Nama, dan NIK wajib diisi!")
    elif not no_urut.isdigit():
        st.warning("⚠️ No Urut harus angka!")
    elif not nik.isdigit() or len(nik) != 16:
        st.warning("⚠️ NIK harus 16 digit angka!")
    elif cek_nik_ganda(sheet, nik) and not st.session_state.edit_mode:
        st.error("❌ NIK sudah pernah diinput!")
    else:
        data = [
            generate_id(),
            str(st.session_state.no_kk).strip(),
            no_urut,
            nama,
            f"'{nik}",
            keberadaan,
            jk,
            tanggal_lahir.strftime('%m/%d/%Y'),
            umur,
            ijazah,
            status,
            shdk,
            status_pekerjaan,
            pekerjaan,
            lapangan,
            catatan
        ]
        try:
            if st.session_state.edit_mode:
                update_berdasarkan_nik(sheet, st.session_state.edit_nik, data)
                st.session_state.flash_message = "✅ Data berhasil diupdate!"
                st.session_state.edit_mode = False
                for k in list(st.session_state.keys()):
                    if k.startswith("edit_"):
                        del st.session_state[k]
            else:
                simpan_ke_sheets(sheet, data, st.session_state.no_kk, shdk)
                st.session_state.flash_message = "✅ Data berhasil disimpan!"
                st.session_state.anggota_data.append(data)
                if st.session_state.anggota_ke < st.session_state.jumlah_anggota:
                    st.session_state.anggota_ke += 1
            st.rerun()
        except Exception as e:
            st.error(f"❌ Gagal menyimpan: {e}")

# ✅ Tampilkan pesan sukses
if "flash_message" in st.session_state:
    st.success(st.session_state.flash_message)
    del st.session_state.flash_message

# 🔙 Navigasi kembali
if st.button("🔙 Kembali ke Form Keluarga"):
    st.switch_page("pages/2_form_keluarga.py")
    for key in ["anggota_ke", "jumlah_anggota", "anggota_data", "no_kk"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
