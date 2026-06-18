import streamlit as st
import requests
import json
import folium
from streamlit_folium import st_folium
from datetime import datetime
import matplotlib.pyplot as plt

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Hero Kebersihan AI - Executive",
    page_icon="♻️",
    layout="wide"
)

# Ambil API Key dari Secrets Streamlit
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "MASUKKAN_API_KEY_ANDA")

# DATABASE PENGGUNA PBT (8 PBT Terengganu)
USERS_PBT = {
    "admin_kt": {"nama": "MB Kuala Terengganu", "pass": "PBT2026"},
    "admin_kn": {"nama": "MP Kuala Nerus", "pass": "PBT2026"},
    "admin_marang": {"nama": "MD Marang", "pass": "PBT2026"},
    "admin_besut": {"nama": "MD Besut", "pass": "PBT2026"},
    "admin_setiu": {"nama": "MD Setiu", "pass": "PBT2026"},
    "admin_hulu": {"nama": "MD Hulu Terengganu", "pass": "PBT2026"},
    "admin_dungun": {"nama": "MP Dungun", "pass": "PBT2026"},
    "admin_kemaman": {"nama": "MP Kemaman", "pass": "PBT2026"},
}

# INITIALIZE DATABASE ADUAN MASTER
if 'db_aduan' not in st.session_state:
    st.session_state.db_aduan = [
        {"ID": "ADU-001", "Tarikh": "2026-06-15", "Kawasan": "Kuala Terengganu", "Kategori": "Sisa Pukal", "Risiko": "Tinggi", "Lat": 5.3302, "Lon": 103.1408, "Status": "Dalam Tindakan", "Nama": "Ahmad Bin Ali", "Telefon": "012-3456789", "Emel": "ahmad@email.com", "Catatan": "Sisa perabot lama dibuang tepi simpang."},
        {"ID": "ADU-002", "Tarikh": "2026-06-16", "Kawasan": "Marang", "Kategori": "Sisa Plastik", "Risiko": "Rendah", "Lat": 5.2114, "Lon": 103.2144, "Status": "Selesai", "Nama": "Siti Aminah", "Telefon": "019-9876543", "Emel": "siti@email.com", "Catatan": "Botol plastik menyumbat parit taman."},
        {"ID": "ADU-003", "Tarikh": "2026-06-17", "Kawasan": "Kuala Nerus", "Kategori": "Sisa Domestik", "Risiko": "Sederhana", "Lat": 5.3660, "Lon": 103.1020, "Status": "Baru", "Nama": "Zulkifli", "Telefon": "013-4455667", "Emel": "zul@email.com", "Catatan": "Sampah dapur berbau melimpah."},
        {"ID": "ADU-004", "Tarikh": "2026-06-18", "Kawasan": "Kemaman", "Kategori": "Sisa Elektronik", "Risiko": "Tinggi", "Lat": 4.2260, "Lon": 103.4240, "Status": "Baru", "Nama": "Wan Mohd", "Telefon": "011-232345", "Emel": "wan@email.com", "Catatan": "Bateri dan komponen TV lama rosak."}
    ]

if 'auth' not in st.session_state:
    st.session_state.auth = {"logged_in": False, "user": None, "pbt_name": ""}

# ==========================================
# 2. FUNGSI AI (GROQ VISION)
# ==========================================
def analisa_gambar_dengan_ai(image_bytes):
    import base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    prompt = "Identify waste category and risk level (Rendah, Sederhana, Tinggi). Respond ONLY with JSON: {\"kategori\": \"...\", \"risiko\": \"...\"}"
    payload = {
        "model": "llama-3.2-11b-vision-preview",
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
    }
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        ai_message = response.json()['choices'][0]['message']['content']
        return json.loads(ai_message.strip())
    except:
        return {"kategori": "Sisa Domestik (Simulasi)", "risiko": "Sederhana"}

# ==========================================
# 3. ANTARA MUKA (SIDEBAR)
# ==========================================
st.sidebar.title("📌 Menu Hero Kebersihan")
mode = st.sidebar.selectbox(
    "Pilih Mod Akses:", 
    ["📊 Dashboard Eksekutif (Pengurusan)", "📱 Portal Awam (Sukarelawan)", "🏢 Login PBT Admin"]
)

if st.session_state.auth["logged_in"]:
    st.sidebar.success(f"Log Masuk: {st.session_state.auth['pbt_name']}")
    if st.sidebar.button("Log Keluar"):
        st.session_state.auth = {"logged_in": False, "user": None, "pbt_name": ""}
        st.rerun()

# ------------------------------------------
# MOD 1: DASHBOARD EKSEKUTIF (MENGGUNAKAN CARTA PAI)
# ------------------------------------------
if mode == "📊 Dashboard Eksekutif (Pengurusan)":