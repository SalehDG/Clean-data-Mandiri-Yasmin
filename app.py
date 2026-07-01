import streamlit as st
import pandas as pd
import re

# Mengatur tampilan halaman web
st.set_page_config(page_title="Perapih Data CSV", layout="wide")
st.title("✨ Aplikasi Perapih Data CSV")
st.write("Silakan upload file CSV mentah.")

# Fungsi untuk membersihkan teks Uraian
def bersihkan_uraian(teks):
    if pd.isna(teks):
        return teks
    teks_bersih = str(teks)
    
    # 1. Hapus pola nomor surat/invoice (contoh: 13/SPM/DRN5/VI/2026)
    # Mencari pola angka yang diikuti garis miring dan karakter lainnya
    teks_bersih = re.sub(r'\d+/[A-Za-z0-9/-]+', '', teks_bersih)
    
    # 2. Hapus pola tanggal (contoh: "2 juni 26" atau menempel seperti "baku2 juni 26")
    # Mencari angka (opsional), spasi, nama bulan, dan angka tahun di akhir teks
    bulan = r'(januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember|jan|feb|mar|apr|jun|jul|agu|sep|okt|nov|des)'
    pola_tanggal = r'\d*\s*' + bulan + r'\s*\d{2,4}$'
    teks_bersih = re.sub(pola_tanggal, '', teks_bersih, flags=re.IGNORECASE)
    
    # Hapus sisa spasi berlebih di awal atau akhir kalimat
    return teks_bersih.strip()

def bersihkan_nominal(angka):
    if pd.isna(angka):
        return angka
    
    # Jika isi sel sama persis dengan ".00", maka jadikan kosong
    if str(angka).strip() == '.00':
        return ""
        
    # Jika tidak, kembalikan angka/teks seperti aslinya
    return angka

# Area Upload File
file_unggahan = st.file_uploader("Upload File CSV Mentah (.csv)", type=["csv"])

if file_unggahan is not None:
    # Membaca file CSV yang diunggah
    df = pd.read_csv(file_unggahan)
    
    st.write("### Data Mentah (Sebelum Diproses):")
    st.dataframe(df.head())

    st.divider()
    
    # Tombol Eksekusi
    if st.button("Proses & Rapihkan Data"):
        # Membuat keranjang (dataframe) baru yang kosong khusus untuk hasil rapih
        df_rapih = pd.DataFrame()
        
        try:
            # 1. Memindahkan kolom 'date' ke 'TGL/ BLN/THN' (Mentah tanpa diubah)
            df_rapih['TGL/ BLN/THN'] = df['Date']
            
            # 2. Membersihkan kolom 'desc' dan memasukkannya ke 'Uraian'
            df_rapih['Uraian'] = df['Description.1'].apply(bersihkan_uraian)
            
            # 3. Menukar posisi Credit dan Debet
            # Kolom Debet yang baru diisi dari kolom Credit yang lama, begitu sebaliknya
            df_rapih['Debit'] = df['Credit'].apply(bersihkan_nominal)
            df_rapih['Credit'] = df['Debit'].apply(bersihkan_nominal)
            
            st.success("✅ Data berhasil dirapihkan!")
            
            st.write("### Data Hasil (Setelah Diproses):")
            st.dataframe(df_rapih.head())
            
            # Tombol Download CSV Bersih
            csv_bersih = df_rapih.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download CSV Rapih",
                data=csv_bersih,
                file_name='data_sudah_rapih.csv',
                mime='text/csv',
            )
            
        except KeyError as error_kolom:
            st.error(f"⚠️ Terjadi kesalahan: Kolom {error_kolom} tidak ditemukan di CSV mentahmu. Pastikan nama kolom pada CSV aslinya sama persis (huruf besar/kecil sangat berpengaruh).")