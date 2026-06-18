import streamlit as st
import requests
import json
import folium
from streamlit_folium import st_folium
from datetime import datetime

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Hero Kebersihan AI",
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

# INITIALIZE DATABASE ADUAN
if 'db_aduan' not in st.session_state:
    st.session_state.db_aduan = [
        {"ID": "ADU-001", "Tarikh": "2026-06-15", "Kawasan": "Kuala Terengganu", "Kategori": "Sisa Pukal", "Risiko": "Tinggi", "Lat": 5.3302, "Lon": 103.1408, "Status": "Dalam Tindakan"},
        {"ID": "ADU-002", "Tarikh": "2026-06-16", "Kawasan": "Marang", "Kategori": "Sisa Plastik", "Risiko": "Rendah", "Lat": 5.2114, "Lon": 103.2144, "Status": "Selesai"}
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
# 3. ANTARA MUKA (SIDEBAR & LOGIN)
# ==========================================
st.sidebar.title("📌 Menu Hero Kebersihan")
mode = st.sidebar.selectbox("Pilih Mod Akses:", ["📱 Portal Awam (Sukarelawan)", "🏢 Login PBT Admin"])

# FUNGSI LOGOUT
if st.session_state.auth["logged_in"]:
    st.sidebar.success(f"Log Masuk: {st.session_state.auth['pbt_name']}")
    if st.sidebar.button("Log Keluar"):
        st.session_state.auth = {"logged_in": False, "user": None, "pbt_name": ""}
        st.rerun()

# ------------------------------------------
# MOD A: PORTAL AWAM
# ------------------------------------------
if mode == "📱 Portal Awam (Sukarelawan)":
    st.title("♻️ Hero Kebersihan: Lapor & Bersih")
    st.info("Laporkan lokasi sampah haram untuk tindakan segera PBT anda.")
    
    with st.form("borang_aduan", clear_on_submit=True):
        kawasan = st.selectbox("Daerah:", ["Kuala Terengganu", "Kuala Nerus", "Marang", "Besut", "Setiu", "Hulu Terengganu", "Dungun", "Kemaman"])
        col_lat, col_lon = st.columns(2)
        lat = col_lat.number_input("Lat:", value=5.3300, format="%.4f")
        lon = col_lon.number_input("Lon:", value=103.1400, format="%.4f")
        gambar = st.file_uploader("Gambar Sisa:", type=["jpg", "png", "jpeg"])
        hantar = st.form_submit_button("Hantar Laporan AI")
        
        if hantar and gambar:
            with st.spinner("AI sedang menganalisis..."):
                hasil_ai = analisa_gambar_dengan_ai(gambar.getvalue())
                rekod = {
                    "ID": f"ADU-00{len(st.session_state.db_aduan)+1}",
                    "Tarikh": datetime.today().strftime('%Y-%m-%d'),
                    "Kawasan": kawasan,
                    "Kategori": hasil_ai.get("kategori"),
                    "Risiko": hasil_ai.get("risiko"),
                    "Lat": lat, "Lon": lon, "Status": "Baru"
                }
                st.session_state.db_aduan.append(rekod)
                st.success("Aduan berjaya dihantar!")
                st.json(hasil_ai)

# ------------------------------------------
# MOD B: LOGIN & DASHBOARD PBT
# ------------------------------------------
elif mode == "🏢 Login PBT Admin":
    if not st.session_state.auth["logged_in"]:
        st.title("🔐 Log Masuk Pegawai PBT")
        with st.form("login_form"):
            user_input = st.text_input("ID Pengguna PBT:")
            pass_input = st.text_input("Kata Laluan:", type="password")
            submit_login = st.form_submit_button("Masuk")
            
            if submit_login:
                if user_input in USERS_PBT and USERS_PBT[user_input]["pass"] == pass_input:
                    st.session_state.auth = {
                        "logged_in": True, 
                        "user": user_input, 
                        "pbt_name": USERS_PBT[user_input]["nama"]
                    }
                    st.success("Log masuk berjaya!")
                    st.rerun()
                else:
                    st.error("ID atau Kata Laluan Salah!")
    else:
        # DASHBOARD ADMIN (HANYA MUNCUL JIKA LOGGED IN)
        st.title(f"🏢 Dashboard Operasi {st.session_state.auth['pbt_name']}")
        
        # FILTER DATA MENGIKUT DAERAH PBT (Opsional: Admin KT hanya nampak KT)
        # Untuk demo, kita tunjuk semua tapi boleh filter jika mahu.
        full_data = st.session_state.db_aduan
        
        # KPI KECIL
        col1, col2, col3 = st.columns(3)
        col1.metric("Jumlah Aduan", len(full_data))
        col2.metric("Kes Baru", len([r for r in full_data if r["Status"]=="Baru"]))
        col3.metric("Selesai", len([r for r in full_data if r["Status"]=="Selesai"]))
        
        st.markdown("---")
        st.subheader("📍 Peta Lokasi Hotspot Sisa")
        m = folium.Map(location=[5.33, 103.14], zoom_start=9)
        for r in full_data:
            warna = "red" if r["Risiko"]=="Tinggi" else "green"
            folium.Marker([r["Lat"], r["Lon"]], popup=f"{r['ID']}: {r['Status']}", icon=folium.Icon(color=warna)).add_to(m)
        st_folium(m, width=1000, height=400)
        
        st.markdown("---")
        st.subheader("📋 Senarai Aduan & Tindakan")
        st.table(full_data)
        
        # UPDATE STATUS
        with st.expander("Update Status Tindakan Lori"):
            id_pilih = st.selectbox("Pilih ID Aduan:", [r["ID"] for r in full_data])
            status_baru = st.selectbox("Tukar Status:", ["Baru", "Dalam Tindakan", "Selesai"])
            if st.button("Simpan Status"):
                for r in st.session_state.db_aduan:
                    if r["ID"] == id_pilih:
                        r["Status"] = status_baru
                st.success(f"Status {id_pilih} dikemaskini!")
                st.rerun()