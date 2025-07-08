import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# ==== KONFIGURASI GOOGLE SHEETS ====
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SPREADSHEET_ID = '1H20OpR06u363DaqJySUGi3yvCXLZ1Oq7VVdscHx_Gx4'

# ==== AUTENTIKASI ====
creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_ID)

# ==== AMBIL DATA MASTER ====
sheet_master = spreadsheet.worksheet("MasterData")
df_master = pd.DataFrame(sheet_master.get_all_records())

sheet_checklist = spreadsheet.worksheet("ChecklistJabatan")
df_checklist = pd.DataFrame(sheet_checklist.get_all_records())

# ==== FORM ====
st.title("📋 Evaluasi Produktivitas Karyawan NBC")

with st.form("form_evaluasi"):
    st.subheader("Isi Form Evaluasi")
    
    periode = st.date_input("Periode Penilaian", format="YYYY-MM", value=datetime.now()).strftime("%Y-%m")
    divisi = st.selectbox("Pilih Divisi", df_master["Divisi"].unique())
    jabatan = st.selectbox("Pilih Jabatan", df_master[df_master["Divisi"] == divisi]["Jabatan"].unique())

    filtered_names = df_master[(df_master["Divisi"] == divisi) & (df_master["Jabatan"] == jabatan)]["Nama Karyawan"].tolist()
    nama_karyawan = st.selectbox("Pilih Nama Karyawan", filtered_names)

    checklist_items = df_checklist[df_checklist["Jabatan"] == jabatan]["Checklist"].tolist()

    st.write("Checklist Penilaian:")
    hasil_checklist = {}
    for item in checklist_items:
        hasil_checklist[item] = st.checkbox(item)

    submitted = st.form_submit_button("✅ Simpan Evaluasi")

# ==== SIMPAN KE SPREADSHEET ====
if submitted:
    sheet_evaluasi = spreadsheet.worksheet("EvaluasiKaryawan")

    now = datetime.now().strftime("%Y-%m-%d")
    rows = []

    for item, is_checked in hasil_checklist.items():
        rows.append([now, periode, divisi, jabatan, nama_karyawan, item, "✓" if is_checked else "✗"])

    sheet_evaluasi.append_rows(rows)
    st.success(f"✅ Evaluasi untuk {nama_karyawan} berhasil disimpan.")
