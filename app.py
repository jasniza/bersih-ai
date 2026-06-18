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
    "admin_bes`ut": {"nama": "MD Besut", "pass": "PBT2026"},
    "admin_setiu": {"nama": "MD Setiu", "pass": "PBT2026"},
    "admin_hulu": {"nama": "MD Hulu Terengganu", "pass": "PBT2026"},
    "admin_dungun": {"nama": "MP Dungun", "pass": "PBT2026"},
    "admin_kemaman": {"nama": "MP Kemaman", "pass": "PBT2026"},
}

# INITIALIZE DATABASE ADUAN (Ditambah Lajur Maklumat Pengadu)
if 'db_aduan' not in st.session_state:
    st.session_state.db_aduan = [
        {
            "ID": "ADU-001", 
            "Tarikh": "2026-06-15", 
            "Kawasan": "Kuala Terengganu", 
            "Kategori": "Sisa Pukal", 
            "Risiko": "Tinggi", 
            "Lat": 5.3302, 
            "Lon": 103.1408, 
            "Status": "Dalam Tindakan",
            "Nama": "Ahmad Bin Ali",
            "Telefon": "012-3456789",
            "Emel": "ahmad@email.com",
            "Catatan": "Sisa perabot lama dibuang di tepi jalan besar berhampiran simpang tiga."
        },
        {
            "ID": "ADU-002", 
            "Tarikh": "2026-06-16", 
            "Kawasan": "Marang", 
            "Kategori": "Sisa Plastik", 
            "Risiko": "Rendah", 
            "Lat": 5.2114, 
            "Lon": 103.2144, 
            "Status": "Selesai",
            "Nama": "Siti Aminah",
            "Telefon": "019-9876543",
            "Emel": "siti@email.com",
            "Catatan": "Banyak botol plastik tersumbat dalam parit utama taman."
        }
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

if st.session_state.auth["logged_in"]:
    st.sidebar.success(f"Log Masuk: {st.session_state.auth['pbt_name']}")
    if st.sidebar.button("Log Keluar"):
        st.session_state.auth = {"logged_in": False, "user": None, "pbt_name": ""}
        st.rerun()

# ------------------------------------------
# MOD A: PORTAL AWAM (PRO)
# ------------------------------------------
if mode == "📱 Portal Awam (Sukarelawan)":
    st.title("♻️ Hero Kebersihan: Lapor & Bersih")
    st.subheader("Aduan Sampah Haram Terengganu")
    st.info("💡 **Cara Tetapkan Lokasi:** Sila klik/ketik pada peta di bawah untuk menanda lokasi longgokan sampah sebelum mengisi borang aduan.")
    
    if 'click_coord' not in st.session_state:
        st.session_state.click_coord = (5.3300, 103.1400)
        
    st.markdown("### 📍 Langkah 1: Ketik Lokasi Pada Peta")
    
    m_user = folium.Map(location=st.session_state.click_coord, zoom_start=11)
    folium.Marker(
        location=st.session_state.click_coord,
        popup="Lokasi Sampah Terpilih",
        icon=folium.Icon(color="red", icon="exclamation-sign")
    ).add_to(m_user)
    
    peta_klik = st_folium(m_user, width="100%", height=350, key="peta_aduan_terbuka")
    
    if peta_klik and peta_klik.get("last_clicked"):
        st.session_state.click_coord = (peta_klik["last_clicked"]["lat"], peta_klik["last_clicked"]["lng"])

    st.markdown("---")
    
    with st.form("borang_aduan_bersih", clear_on_submit=True):
        st.markdown("### 📝 Langkah 2: Butiran Aduan & Maklumat Pengadu")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            nama_input = st.text_input("👤 Nama Penuh Pengadu:", placeholder="Contoh: Ali bin Abu")
            tel_input = st.text_input("📞 No. Telefon Bimbit:", placeholder="Contoh: 01X-XXXXXXX")
        with col_f2:
            emel_input = st.text_input("✉️ Alamat Emel:", placeholder="Contoh: ali@email.com")
            kawasan = st.selectbox("Daerah Kejadian:", ["Kuala Terengganu", "Kuala Nerus", "Marang", "Besut", "Setiu", "Hulu Terengganu", "Dungun", "Kemaman"])
            
        catatan_input = st.text_area("✍️ Catatan Tambahan / Deskripsi Lokasi:", placeholder="Berikan info tambahan seperti berdekatan tiang lampu, kedai makan, tanda tempat dll...")
        
        st.write(f"📌 **Koordinat Terkunci:** Latitude: `{st.session_state.click_coord[0]:.4f}` | Longitude: `{st.session_state.click_coord[1]:.4f}`")
        
        gambar = st.file_uploader("📸 Muat naik gambar bukti longgokan sampah:", type=["jpg", "png", "jpeg"])
        hantar = st.form_submit_button("🚀 Hantar Laporan Ke Enjin AI")
        
        if hantar:
            if gambar is not None and nama_input and tel_input:
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
                        "Status": "Baru",
                        "Nama": nama_input,
                        "Telefon": tel_input,
                        "Emel": emel_input if emel_input else "Tiada",
                        "Catatan": catatan_input if catatan_input else "Tiada catatan tambahan."
                    }
                    st.session_state.db_aduan.append(rekod)
                    st.success(f"🎉 Syabas {nama_input}! Aduan {id_baru} berjaya dihantar ke sistem {kawasan}.")
                    
                    st.subheader("🤖 Hasil Imbasan AI Masa-Nyata:")
                    col_res1, col_res2 = st.columns(2)
                    col_res1.metric(label="Kategori Sisa Dikesan", value=hasil_ai.get("kategori"))
                    col_res2.metric(label="Tahap Risiko / Volum", value=hasil_ai.get("risiko"))
            else:
                st.error("❌ Sila pastikan Nama, No. Telefon dan Gambar Bukti diisi sebelum hantar!")

# ------------------------------------------
# MOD B: DASHBOARD ADMIN PBT PRO
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
                    st.session_state.auth = {"logged_in": True, "user": user_input, "pbt_name": USERS_PBT[user_input]["nama"]}
                    st.success("Log masuk berjaya!")
                    st.rerun()
                else:
                    st.error("ID atau Kata Laluan Salah!")
    else:
        pbt_full_name = st.session_state.auth['pbt_name']
        daerah_tapis = pbt_full_name.replace("MB ", "").replace("MP ", "").replace("MD ", "")
        
        st.title(f"🏢 Dashboard Operasi {pbt_full_name}")
        st.subheader(f"Pengurusan Sisa Haram Daerah {daerah_tapis}")
        
        data_daerah_sahaja = [r for r in st.session_state.db_aduan if r["Kawasan"] == daerah_tapis]
        
        col1, col2, col3 = st.columns(3)
        col1.metric(f"Jumlah Aduan {daerah_tapis}", len(data_daerah_sahaja))
        col2.metric("Kes Baru", len([r for r in data_daerah_sahaja if r["Status"]=="Baru"]))
        col3.metric("Selesai", len([r for r in data_daerah_sahaja if r["Status"]=="Selesai"]))
        
        st.markdown("---")
        st.subheader("📍 Peta Lokasi Hotspot Sisa Daerah")
        
        map_center = [5.33, 103.14]
        if data_daerah_sahaja:
            map_center = [data_daerah_sahaja[0]["Lat"], data_daerah_sahaja[0]["Lon"]]
            
        m = folium.Map(location=map_center, zoom_start=11)
        for r in data_daerah_sahaja:
            warna = "red" if r["Risiko"]=="Tinggi" else "orange" if r["Risiko"]=="Sederhana" else "green"
            folium.Marker([r["Lat"], r["Lon"]], popup=f"{r['ID']}", icon=folium.Icon(color=warna)).add_to(m)
        st_folium(m, width="100%", height=350, key="peta_admin_daerah")
        
        st.markdown("---")
        st.subheader("📋 Senarai Aduan & Profil Pengadu")
        
        if not data_daerah_sahaja:
            st.info(f"Alhamdulillah, tiada aduan aktif di daerah {daerah_tapis}.")
        else:
            for aduan in data_daerah_sahaja:
                with st.container():
                    col_info, col_pengadu, col_img, col_action = st.columns([2, 2, 2, 1])
                    
                    with col_info:
                        st.markdown(f"### 🆔 {aduan['ID']}")
                        st.write(f"📅 **Tarikh:** {aduan['Tarikh']}")
                        st.write(f"🚯 **Kategori AI:** {aduan['Kategori']}")
                        if aduan['Risiko'] == "Tinggi":
                            st.error(f"🚨 **Risiko:** {aduan['Risiko']}")
                        elif aduan['Risiko'] == "Sederhana":
                            st.warning(f"⚠️ **Risiko:** {aduan['Risiko']}")
                        else:
                            st.success(f"✅ **Risiko:** {aduan['Risiko']}")
                        st.write(f"📍 **Koordinat:** `{aduan['Lat']:.4f}, {aduan['Lon']:.4f}`")
                    
                    with col_pengadu:
                        st.markdown("🗣️ **Maklumat Pengadu:**")
                        st.write(f"👤 **Nama:** {aduan.get('Nama', 'Anonym')}")
                        st.write(f"📞 **No. Tel:** {aduan.get('Telefon', 'Tiada')}")
                        st.write(f"✉️ **Emel:** {aduan.get('Emel', 'Tiada')}")
                        st.info(f"💬 **Catatan:**\n\n{aduan.get('Catatan', 'Tiada')}")
                    
                    with col_img:
                        st.markdown("**📸 Gambar Lapangan:**")
                        if aduan['ID'] in ["ADU-001", "ADU-002"]:
                            st.image("https://images.unsplash.com/photo-1611284446314-60a58ac0deb9?w=400", width=200)
                        else:
                            st.info("🖼️ Gambar fizikal sedia pada peranti.")
                    
                    with col_action:
                        st.markdown("**⚡ Status:**")
                        status_warna = "🔵 Baru" if aduan['Status'] == "Baru" else "🟡 Dalam Tindakan" if aduan['Status'] == "Dalam Tindakan" else "🟢 Selesai"
                        st.markdown(f"**Semasa:** {status_warna}")
                        
                        status_baru = st.selectbox("Tukar:", ["Baru", "Dalam Tindakan", "Selesai"], key=f"sel_{aduan['ID']}")
                        if st.button("Kemas Kini", key=f"btn_{aduan['ID']}"):
                            for main_r in st.session_state.db_aduan:
                                if main_r["ID"] == aduan['ID']:
                                    main_r["Status"] = status_baru
                            st.success("Dikemaskini!")
                            st.rerun()
                            
                st.markdown("<hr style='border:1px dashed #ccc'>", unsafe_allow_html=True)