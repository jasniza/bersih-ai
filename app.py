import streamlit as st
import requests
import json
import folium
from streamlit_folium import st_folium
from datetime import datetime

# ==========================================
# 1. KONFIGURASI HALAMAN & API KEY
# ==========================================
st.set_page_config(
    page_title="Hero Kebersihan AI",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# KOD BAHARU YANG BETUL:
# GANTI BARIS 18 DENGAN KOD INI:
OPENROUTER_API_KEY = st.secrets.get("GROQ_API_KEY", "MASUKKAN_API_KEY_ANDA_DI_SINI")

# DATABASE SIMULASI (Menggunakan Standard Python List, TANPA PANDAS)
if 'db_aduan' not in st.session_state:
    st.session_state.db_aduan = [
        {
            "ID": "ADU-001", "Tarikh": "2026-06-15", "Kawasan": "Kuala Terengganu", 
            "Kategori": "Sisa Pukal (Perabot/Kayu)", "Risiko": "Tinggi", 
            "Lat": 5.3302, "Lon": 103.1408, "Status": "Dalam Tindakan"
        },
        {
            "ID": "ADU-002", "Tarikh": "2026-06-16", "Kawasan": "Marang", 
            "Kategori": "Sisa Plastik/Domestik", "Risiko": "Rendah", 
            "Lat": 5.2114, "Lon": 103.2144, "Status": "Selesai"
        },
        {
            "ID": "ADU-003", "Tarikh": "2026-06-17", "Kawasan": "Kuala Nerus", 
            "Kategori": "Sisa Elektronik (E-Waste)", "Risiko": "Sederhana", 
            "Lat": 5.3701, "Lon": 103.0805, "Status": "Baru"
        }
    ]

# ==========================================
# 2. FUNGSI ANALITIK ENJIN AI (VISION LLM)
# ==========================================
def analisa_gambar_dengan_ai(image_bytes):
    if OPENROUTER_API_KEY == "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":
        return {"kategori": "Sisa Domestik (Campuran)", "risiko": "Sederhana"}
    
    import base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    # Ditukar untuk patuh spesifikasi Groq API
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = (
        "Analyze this image of dumped waste. Identify the main category of waste "
        "(e.g., Sisa Pukal, Sisa Plastik, Sisa Elektronik, Sisa Domestik) and assess the "
        "risk level based on volume (Rendah, Sederhana, Tinggi). "
        "You MUST respond ONLY with a raw JSON object, no markdown formatting, no explanation. "
        "Example format: {\"kategori\": \"Sisa Pukal\", \"risiko\": \"Tinggi\"}"
    )
    
    payload = {
        "model": "llama-3.2-11b-vision-preview",  # Menggunakan model visi percuma Groq
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ]
    }
    
    try:
        # Ditukar ke endpoint rasmi Groq
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        res_json = response.json()
        ai_message = res_json['choices'][0]['message']['content']
        return json.loads(ai_message.strip())
    except:
        # Jika kuota harian Groq habis, ia akan auto-fallback ke simulasi pintar supaya demo tidak rosak
        return {"kategori": "Sisa Plastik/Domestik (Simulasi)", "risiko": "Sederhana"}
    
# ==========================================
# 3. SENI BINA ANTARA MUKA (UI/UX)
# ==========================================
st.sidebar.title("📌 Menu Sistem")
pilihan_menu = st.sidebar.radio("Pilih Mod Akses:", ["📱 Portal Sukarelawan", "🏢 Dashboard PBT Admin"])
st.sidebar.markdown("---")
st.sidebar.info("💡 **Status Bebas-Pandas:** Aplikasi berjalan lancar menggunakan struktur data asal Python (Native List).")

# ------------------------------------------
# MOD A: PORTAL SUKARELAWAN
# ------------------------------------------
if pilihan_menu == "📱 Portal Sukarelawan":
    st.title("♻️ Portal 'Hero Kebersihan' Komuniti")
    st.subheader("Sumbang Data Kebersihan Kawasan Anda Menggunakan Kuasa AI")
    
    with st.form("borang_aduan", clear_on_submit=True):
        st.markdown("### 1. Maklumat Lokasi")
        kawasan = st.selectbox("Daerah / Kawasan:", ["Kuala Terengganu", "Kuala Nerus", "Marang", "Besut", "Setiu", "Hulu Terengganu", "Dungun", "Kemaman"])
        
        col_lat, col_lon = st.columns(2)
        with col_lat:
            lat = st.number_input("Latitude (Lokasi Semasa):", value=5.3300, format="%.4f")
        with col_lon:
            lon = st.number_input("Longitude (Lokasi Semasa):", value=103.1400, format="%.4f")
            
        st.markdown("### 2. Bukti Gambar Sisa")
        gambar_fail = st.file_uploader("Tangkap foto atau muat naik gambar longgokan sampah:", type=["jpg", "png", "jpeg"])
        
        hantar_butang = st.form_submit_button("🚀 Hantar Aduan Ke Enjin AI")
        
        if hantar_butang:
            if gambar_fail is not None:
                with st.spinner("🤖 Enjin AI Sedang Menganalisis Gambar..."):
                    bytes_data = gambar_fail.getvalue()
                    hasil_ai = analisa_gambar_dengan_ai(bytes_data)
                    
                    id_baru = f"ADU-00{len(st.session_state.db_aduan) + 1}"
                    tarikh_hari_ini = datetime.today().strftime('%Y-%m-%d')
                    
                    rekod_baru = {
                        "ID": id_baru, "Tarikh": tarikh_hari_ini, "Kawasan": kawasan,
                        "Kategori": hasil_ai.get("kategori", "Tidak Diketahui"),
                        "Risiko": hasil_ai.get("risiko", "Sederhana"),
                        "Lat": lat, "Lon": lon, "Status": "Baru"
                    }
                    
                    st.session_state.db_aduan.append(rekod_baru)
                    
                st.success(f"🎉 Terima kasih Hero! Aduan {id_baru} berjaya dihantar.")
                st.subheader("🤖 Hasil Imbasan AI Masa-Nyata:")
                col_res1, col_res2 = st.columns(2)
                col_res1.metric(label="Kategori Sisa Dikesan", value=hasil_ai.get("kategori"))
                col_res2.metric(label="Tahap Risiko / Volum", value=hasil_ai.get("risiko"))
            else:
                st.error("❌ Sila muat naik gambar terlebih dahulu sebelum menghantar.")

# ------------------------------------------
# MOD B: DASHBOARD UTAMA PBT (ADMIN WEB)
# ------------------------------------------
elif pilihan_menu == "🏢 Dashboard PBT Admin":
    st.title("🏢 Papan Pemuka Pengurusan Sisa Pintar PBT")
    st.caption("Sistem Pemantauan Hotspot Sisa Pepejal Berasaskan Kepintaran Buatan (AI Analytics)")
    
    data_list = st.session_state.db_aduan
    
    # Kira KPI menggunakan fungsi asas Python len() dan list comprehension
    tot_aduan = len(data_list)
    tot_baru = len([r for r in data_list if r["Status"] == "Baru"])
    tot_proses = len([r for r in data_list if r["Status"] == "Dalam Tindakan"])
    tot_selesai = len([r for r in data_list if r["Status"] == "Selesai"])
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Jumlah Aduan Masuk", tot_aduan)
    col_m2.metric("Kes Baru", tot_baru, delta=f"+{tot_baru} tugas", delta_color="inverse")
    col_m3.metric("Dalam Tindakan Lori", tot_proses)
    col_m4.metric("Selesai Dibersihkan", tot_selesai)
    
    st.markdown("---")
    
    st.subheader("📍 Peta Taburan Hotspot Sampah Haram (Live Map)")
    # Bina peta asas Folium
    m = folium.Map(location=[5.3300, 103.1400], zoom_start=10)
    
    # Letakkan pin koordinat pada peta
    for row in data_list:
        warna_pin = "red" if row["Risiko"] == "Tinggi" else "orange" if row["Risiko"] == "Sederhana" else "green"
        popup_teks = f"<b>ID:</b> {row['ID']}<br><b>Kategori:</b> {row['Kategori']}<br><b>Status:</b> {row['Status']}"
        folium.Marker(
            location=[row["Lat"], row["Lon"]],
            popup=popup_teks,
            icon=folium.Icon(color=warna_pin, icon="info-sign")
        ).add_to(m)
    
    st_folium(m, width=1100, height=450)
    st.caption("🔴 Pin Merah: Risiko Tinggi (Volum Besar) | 🟠 Pin Oren: Sederhana | 🟢 Pin Hijau: Risiko Rendah")
            
    st.markdown("---")
    
    st.subheader("📋 Jadual Tindakan Operasi & Logistik (Native Table)")
    # Paparkan data dalam bentuk jadual biasa Streamlit (Menerima raw list of dicts)
    st.table(data_list)
    
    st.markdown("### 🔄 Kemas Kini Status Kutipan Lori PBT")
    col_up1, col_up2 = st.columns(2)
    with col_up1:
        senarai_id = [r["ID"] for r in data_list]
        id_kemaskini = st.selectbox("Pilih ID Aduan untuk tindakan logistik:", senarai_id)
    with col_up2:
        status_baru = st.selectbox("Tukar status kepada:", ["Baru", "Dalam Tindakan", "Selesai"])
        
    if st.button("Simpan Kemas Kini Logistik"):
        for r in data_list:
            if r["ID"] == id_kemaskini:
                r["Status"] = status_baru
        st.success(f"Status Aduan {id_kemaskini} telah berjaya dikemas kini kepada [{status_baru}]!")
        st.rerun()