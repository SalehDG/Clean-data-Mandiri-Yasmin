import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Mengatur tampilan halaman web
st.set_page_config(page_title="Perapih Data Excel", layout="wide")
st.title("✨ Aplikasi Perapih Data")
st.write("Silakan upload file Excel mentah (.xlsx).")

# Fungsi untuk membersihkan teks Uraian
def bersihkan_uraian(teks):
    if pd.isna(teks):
        return teks
    teks_bersih = str(teks)
    
    # 1. Hapus pola nomor surat/invoice (contoh: 13/SPM/DRN5/VI/2026)
    teks_bersih = re.sub(r'\d+/[A-Za-z0-9/-]+', '', teks_bersih)
    
    # 2. Hapus pola tanggal (contoh: "2 juni 26")
    bulan = r'(januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember|jan|feb|mar|apr|jun|jul|agu|sep|okt|nov|des)'
    pola_tanggal = r'\d*\s*' + bulan + r'\s*\d{2,4}$'
    teks_bersih = re.sub(pola_tanggal, '', teks_bersih, flags=re.IGNORECASE)
    
    return teks_bersih.strip()

# Fungsi untuk membersihkan nominal
def bersihkan_nominal(angka):
    if pd.isna(angka):
        return angka
        
    angka_str = str(angka).strip()
    
    # Jika isi sel sama persis dengan ".00" atau ",00"
    if angka_str == '.00' or angka_str == ',00':
        return ""
        
    # Hapus ".00" jika ada di ujung belakang
    if angka_str.endswith(".00"):
        angka_str = angka_str[:-3]
        
    # Ganti sisa koma menjadi titik
    angka_str = angka_str.replace(",", ".")
    
    return angka_str

# Fungsi untuk mengubah tahun 26 menjadi mutlak 2026
def bersihkan_tanggal(tgl):
    if pd.isna(tgl):
        return tgl
    
    tgl_str = str(tgl).strip()
    
    # Cari angka 26 yang didahului oleh '/' atau '-' di ujung kata/kalimat, 
    # dan ubah jadi 2026. Jika sudah 2026 tidak akan tersentuh.
    tgl_str = re.sub(r'([/-])26\b', r'\g<1>2026', tgl_str)
    
    return tgl_str

# Area Upload File
file_unggahan = st.file_uploader("Upload File Excel Mentah (.xlsx)", type=["xlsx"])

if file_unggahan is not None:
    # Membaca file Excel mentah
    df = pd.read_excel(file_unggahan)
    
    st.write("### Data Mentah (Sebelum Diproses):")
    st.dataframe(df.head())

    st.divider()
    
    # Tombol Eksekusi
    if st.button("Proses & Rapihkan Data"):
        df_rapih = pd.DataFrame()
        
        try:
            # 1. Memindahkan kolom 'date' & merapihkan tahunnya jadi 2026
            df_rapih['TGL/ BLN/THN'] = df['Date'].apply(bersihkan_tanggal)
            
            # 2. Membersihkan kolom 'desc' dan memasukkannya ke 'Uraian'
            df_rapih['Uraian'] = df['Description.1'].apply(bersihkan_uraian)
            
            # 3. Menukar posisi Credit dan Debet beserta pembersihan nominal
            df_rapih['Debit'] = df['Credit'].apply(bersihkan_nominal)
            df_rapih['Credit'] = df['Debit'].apply(bersihkan_nominal)
            
            st.success("✅ Data berhasil dirapihkan!")
            
            st.write("### Data Hasil (Setelah Diproses):")
            st.dataframe(df_rapih.head())
            
            # Menyiapkan file Excel untuk didownload
            output = BytesIO()
            df_rapih.to_excel(output, index=False, engine='openpyxl')
            excel_data = output.getvalue()
            
            # Tombol Download Excel Bersih
            st.download_button(
                label="⬇️ Download Excel Rapih",
                data=excel_data,
                file_name='data_sudah_rapih.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
            
        except KeyError as error_kolom:
            st.error(f"⚠️ Terjadi kesalahan: Kolom {error_kolom} tidak ditemukan di Excel mentahmu. Pastikan nama kolom pada aslinya sama persis.")
