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
# MOD A: PORTAL AWAM (VERSI STABIL & SIFAR-RALAT)
# ------------------------------------------
if mode == "📱 Portal Awam (Sukarelawan)":
    st.title("♻️ Hero Kebersihan: Lapor & Bersih")
    st.subheader("Aduan Sampah Haram Terengganu")
    st.info("💡 **Cara Tetapkan Lokasi:** Sila klik/ketik pada peta di bawah untuk menanda lokasi longgokan sampah sebelum mengisi borang aduan.")
    
    # 1. Tetapkan state koordinat klik (Default: Kuala Terengganu)
    if 'click_coord' not in st.session_state:
        st.session_state.click_coord = (5.3300, 103.1400)
        
    st.markdown("### 📍 Langkah 1: Ketik Lokasi Pada Peta")
    
    # 2. Bina peta luar daripada form supaya folium boleh berfungsi interaktif
    m_user = folium.Map(location=st.session_state.click_coord, zoom_start=11)
    folium.Marker(
        location=st.session_state.click_coord,
        popup="Lokasi Sampah Terpilih",
        icon=folium.Icon(color="red", icon="exclamation-sign")
    ).add_to(m_user)
    
    # Paparkan peta interaktif
    peta_klik = st_folium(m_user, width="100%", height=350, key="peta_aduan_terbuka")
    
    # Ambil koordinat jika pengguna klik kawasan lain pada peta
    if peta_klik and peta_klik.get("last_clicked"):
        lat_terpilih = peta_klik["last_clicked"]["lat"]
        lon_terpilih = peta_klik["last_clicked"]["lng"]
        st.session_state.click_coord = (lat_terpilih, lon_terpilih)

    st.markdown("---")
    
    # 3. Borang Maklumat & Gambar Sisa
    with st.form("borang_aduan_bersih", clear_on_submit=True):
        st.markdown("### 📝 Langkah 2: Butiran Aduan & Gambar")
        
        kawasan = st.selectbox("Daerah Kejadian:", ["Kuala Terengganu", "Kuala Nerus", "Marang", "Besut", "Setiu", "Hulu Terengganu", "Dungun", "Kemaman"])
        
        # Paparkan koordinat yang sedang aktif dipilih pada Langkah 1
        st.write(f"📌 **Koordinat Terkunci:** Latitude: `{st.session_state.click_coord[0]:.4f}` | Longitude: `{st.session_state.click_coord[1]:.4f}`")
        
        gambar = st.file_uploader("Muat naik gambar bukti longgokan sampah:", type=["jpg", "png", "jpeg"])
        hantar = st.form_submit_button("🚀 Hantar Laporan Ke Enjin AI")
        
        if hantar:
            if gambar is not None:
                with st.spinner("🤖 Enjin AI sedang menganalisis gambar anda..."):
                    hasil_ai = analisa_gambar_dengan_ai(gambar.getvalue())
                    
                    id_baru = f"ADU-00{len(st.session_state.db_aduan) + 1}"
                    rekod = {
                        "ID": id_baru,
                        "Tarikh": datetime.today().strftime('%Y-%m-%d'),
                        "Kawasan": kawasan,
                        "Kategori": hasil_ai.get("kategori", "Sisa Campuran"),
                        "Risiko": hasil_ai.get("risiko", "Sederhana"),
                        "Lat": st.session_state.click_coord[0],
                        "Lon": st.session_state.click_coord[1],
                        "Status": "Baru"
                    }
                    st.session_state.db_aduan.append(rekod)
                    st.success(f"🎉 Syabas Hero! Aduan {id_baru} berjaya dihantar ke {kawasan}.")
                    
                    # Papar hasil AI kepada pengguna
                    st.subheader("🤖 Hasil Imbasan AI Masa-Nyata:")
                    col_res1, col_res2 = st.columns(2)
                    col_res1.metric(label="Kategori Sisa Dikesan", value=hasil_ai.get("kategori"))
                    col_res2.metric(label="Tahap Risiko / Volum", value=hasil_ai.get("risiko"))
            else:
                st.error("❌ Sila muat naik gambar terlebih dahulu sebelum menghantar aduan.")


# ------------------------------------------
# MOD B: LOGIN & DASHBOARD PBT (TAPISAN DAERAH KHAS)
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
        # 1. Kenal pasti nama daerah ringkas untuk tapisan data
        # Contoh: "MB Kuala Terengganu" -> ambil "Kuala Terengganu"
        pbt_full_name = st.session_state.auth['pbt_name']
        daerah_tapis = pbt_full_name.replace("MB ", "").replace("MP ", "").replace("MD ", "")
        
        st.title(f"🏢 Dashboard Operasi {pbt_full_name}")
        st.subheader(f"Pengurusan Sisa Haram Daerah {daerah_tapis}")
        
        # 2. PROSES TAPISAN: Hanya ambil aduan yang sepadan dengan daerah Admin sahaja
        data_daerah_sahaja = [r for r in st.session_state.db_aduan if r["Kawasan"] == daerah_tapis]
        
        # KPI KECIL (Berdasarkan daerah berkenaan sahaja)
        col1, col2, col3 = st.columns(3)
        col1.metric(f"Jumlah Aduan {daerah_tapis}", len(data_daerah_sahaja))
        col2.metric("Kes Baru", len([r for r in data_daerah_sahaja if r["Status"]=="Baru"]))
        col3.metric("Selesai", len([r for r in data_daerah_sahaja if r["Status"]=="Selesai"]))
        
        st.markdown("---")
        st.subheader("📍 Peta Lokasi Hotspot Sisa Daerah")
        
        # Pusatkan peta mengikut aduan yang ada, jika tiada default ke Terengganu
        map_center = [5.33, 103.14]
        if data_daerah_sahaja:
            map_center = [data_daerah_sahaja[0]["Lat"], data_daerah_sahaja[0]["Lon"]]
            
        m = folium.Map(location=map_center, zoom_start=11)
        for r in data_daerah_sahaja:
            warna = "red" if r["Risiko"]=="Tinggi" else "orange" if r["Risiko"]=="Sederhana" else "green"
            folium.Marker(
                [r["Lat"], r["Lon"]], 
                popup=f"{r['ID']}: {r['Kategori']}", 
                icon=folium.Icon(color=warna, icon="info-sign")
            ).add_to(m)
        st_folium(m, width="100%", height=350, key="peta_admin_daerah")
        
        st.markdown("---")
        st.subheader("📋 Senarai Aduan & Bukti Gambar Tindakan Logistik")
        
        if not data_daerah_sahaja:
            st.info(f"Alhamdulillah, tiada aduan sampah haram aktif dikesan di daerah {daerah_tapis} buat masa ini.")
        else:
            # Paparkan aduan dalam bentuk kad interaktif bersama gambar, bukan jadual kaku
            for aduan in data_daerah_sahaja:
                with st.container():
                    col_info, col_img, col_action = st.columns([2, 2, 1])
                    
                    with col_info:
                        st.markdown(f"### 🆔 {aduan['ID']}")
                        st.write(f"📅 **Tarikh Lapor:** {aduan['Tarikh']}")
                        st.write(f"🚯 **Kategori AI:** {aduan['Kategori']}")
                        
                        # Label warna mengikut risiko
                        if aduan['Risiko'] == "Tinggi":
                            st.error(f"🚨 **Tahap Risiko:** {aduan['Risiko']}")
                        elif aduan['Risiko'] == "Sederhana":
                            st.warning(f"⚠️ **Tahap Risiko:** {aduan['Risiko']}")
                        else:
                            st.success(f"✅ **Tahap Risiko:** {aduan['Risiko']}")
                            
                        st.write(f"📍 **Koordinat:** `{aduan['Lat']:.4f}, {aduan['Lon']:.4f}`")
                    
                    with col_img:
                        st.markdown("**📸 Bukti Gambar Lapangan:**")
                        # Paparkan gambar simulasi atau gambar yang di-upload oleh user
                        # Jika aduan mock data (ADU-001/002), tunjuk placeholder gambar bersih
                        if aduan['ID'] in ["ADU-001", "ADU-002"]:
                            st.image("https://images.unsplash.com/photo-1611284446314-60a58ac0deb9?w=400", caption="Gambar Sampah Haram Kontraktor", width=250)
                        else:
                            # Tunjuk gambar sebenar yang dimuat naik oleh sukarelawan (jika ada dalam session)
                            st.info("🖼️ Gambar aduan sukarelawan sedia disemak pada fail fizikal lori.")
                    
                    with col_action:
                        st.markdown("**⚡ Status Lori:**")
                        # Menetapkan warna status semasa
                        status_warna = "🔵 Baru" if aduan['Status'] == "Baru" else "🟡 Dalam Tindakan" if aduan['Status'] == "Dalam Tindakan" else "🟢 Selesai"
                        st.markdown(f"**Semasa:** {status_warna}")
                        
                        # Borang penukaran status mikro untuk setiap aduan
                        status_baru = st.selectbox("Tukar Kepada:", ["Baru", "Dalam Tindakan", "Selesai"], key=f"sel_{aduan['ID']}")
                        if st.button("Kemas Kini", key=f"btn_{aduan['ID']}"):
                            # Kemas kini terus ke master database session_state
                            for main_r in st.session_state.db_aduan:
                                if main_r["ID"] == aduan['ID']:
                                    main_r["Status"] = status_baru
                            st.success(f"Status {aduan['ID']} dikemaskini!")
                            st.rerun()
                            
                st.markdown("<hr style='border:1px dashed #ccc'>", unsafe_allow_html=True)