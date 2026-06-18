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
    st.title("📊 Sistem Pemantauan Kebersihan Berpusat AI (SUK Terengganu)")
    st.subheader("Analisis Makro Titik Panas & Prestasi Tindakan PBT Negeri")
    st.markdown("---")
    
    master_data = st.session_state.db_aduan
    
    # METRIKS UTAMA NEGERI
    total_kes = len(master_data)
    kes_baru = len([r for r in master_data if r["Status"] == "Baru"])
    kes_proses = len([r for r in master_data if r["Status"] == "Dalam Tindakan"])
    kes_selesai = len([r for r in master_data if r["Status"] == "Selesai"])
    kadar_selesai = (kes_selesai / total_kes * 100) if total_kes > 0 else 100
    
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("📊 Jumlah Kes Keseluruhan", f"{total_kes} Kes")
    m2.metric("🔵 Status: Baru", f"{kes_baru} Kes", delta=f"{kes_baru} aktif", delta_color="inverse")
    m3.metric("🟡 Status: Dalam Tindakan", f"{kes_proses} Kes")
    m4.metric("🟢 Status: Selesai", f"{kes_selesai} Kes")
    m5.metric("📈 KPI Kelulusan Kes", f"{kadar_selesai:.1f}%")
    
    st.markdown("---")
    
    # SEKSYEN ANALISIS GRAFIK STATISTIK
    col_graph1, col_graph2 = st.columns(2)
    
    with col_graph1:
        st.markdown("#### 🏛️ Statistik Pecahan Kes Mengikut Daerah / PBT")
        daerah_counts = {}
        for r in master_data:
            daerah_counts[r["Kawasan"]] = daerah_counts.get(r["Kawasan"], 0) + 1
        st.bar_chart(daerah_counts)
        
    with col_graph2:
        st.markdown("#### 🚯 Jenis Kategori Sisa Utama Dikesan AI (Kadar Peratusan)")
        kategori_counts = {}
        for r in master_data:
            kategori_counts[r["Kategori"]] = kategori_counts.get(r["Kategori"], 0) + 1
            
        if kategori_counts:
            # Bina Carta Pai Menggunakan Matplotlib
            fig, ax = plt.subplots(figsize=(6, 4.5))
            colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0','#ffb3e6']
            
            ax.pie(
                kategori_counts.values(), 
                labels=kategori_counts.keys(), 
                autopct='%1.1f%%', 
                startangle=140, 
                colors=colors[:len(kategori_counts)],
                textprops={'fontsize': 10}
            )
            ax.axis('equal')  # Memastikan carta pai berbentuk bulat sempurna
            fig.patch.set_alpha(0.0)  # Latar belakang lutsinar supaya serasi dengan tema Streamlit
            st.pyplot(fig)
        else:
            st.info("Tiada data kategori sisa untuk dijana.")

    st.markdown("---")
    st.markdown("#### 📍 Pemetaan Real-Time Hotspot Sisa Berisiko Tinggi (Seluruh Negeri)")
    m_executive = folium.Map(location=[5.33, 103.14], zoom_start=8)
    for r in master_data:
        warna = "red" if r["Risiko"] == "Tinggi" else "orange" if r["Risiko"] == "Sederhana" else "green"
        info_pop = f"<b>ID:</b> {r['ID']}<br><b>PBT:</b> {r['Kawasan']}<br><b>Sisa:</b> {r['Kategori']}<br><b>Status:</b> {r['Status']}"
        folium.Marker([r["Lat"], r["Lon"]], popup=folium.Popup(info_pop, max_width=300), icon=folium.Icon(color=warna, icon="cloud")).add_to(m_executive)
    st_folium(m_executive, width="100%", height=400, key="peta_eksekutif_state")

# ------------------------------------------
# MOD 2: PORTAL AWAM
# ------------------------------------------
elif mode == "📱 Portal Awam (Sukarelawan)":
    st.title("♻️ Hero Kebersihan: Lapor & Bersih")
    st.subheader("Aduan Sampah Haram Terengganu")
    st.info("💡 **Cara Tetapkan Lokasi:** Sila klik/ketik pada peta di bawah untuk menanda lokasi longgokan sampah sebelum mengisi borang aduan.")
    
    if 'click_coord' not in st.session_state:
        st.session_state.click_coord = (5.3300, 103.1400)
        
    st.markdown("### 📍 Langkah 1: Ketik Lokasi Pada Peta")
    m_user = folium.Map(location=st.session_state.click_coord, zoom_start=11)
    folium.Marker(location=st.session_state.click_coord, popup="Lokasi Sampah Terpilih", icon=folium.Icon(color="red", icon="exclamation-sign")).add_to(m_user)
    peta_klik = st_folium(m_user, width="100%", height=350, key="peta_aduan_terbuka")
    
    if peta_klik and peta_klik.get("last_clicked"):
        st.session_state.click_coord = (peta_klik["last_clicked"]["lat"], peta_klik["last_clicked"]["lng"])

    st.markdown("---")
    
    with st.form("borang_aduan_bersih", clear_on_submit=True):
        st.markdown("### 📝 Langkah 2: Butiran Aduan & Maklumat Pengadu")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            nama_input = st.text_input("👤 Nama Penuh Pengadu:")
            tel_input = st.text_input("📞 No. Telefon Bimbit:")
        with col_f2:
            emel_input = st.text_input("✉️ Alamat Emel:")
            kawasan = st.selectbox("Daerah Kejadian:", ["Kuala Terengganu", "Kuala Nerus", "Marang", "Besut", "Setiu", "Hulu Terengganu", "Dungun", "Kemaman"])
            
        catatan_input = st.text_area("✍️ Catatan Tambahan / Deskripsi Lokasi:")
        st.write(f"📌 **Koordinat Terkunci:** Latitude: `{st.session_state.click_coord[0]:.4f}` | Longitude: `{st.session_state.click_coord[1]:.4f}`")
        gambar = st.file_uploader("📸 Muat naik gambar bukti longgokan sampah:", type=["jpg", "png", "jpeg"])
        hantar = st.form_submit_button("🚀 Hantar Laporan Ke Enjin AI")
        
        if hantar and gambar and nama_input and tel_input:
            with st.spinner("🤖 Enjin AI sedang menganalisis gambar anda..."):
                hasil_ai = analisa_gambar_dengan_ai(gambar.getvalue())
                id_baru = f"ADU-00{len(st.session_state.db_aduan) + 1}"
                rekod = {
                    "ID": id_baru, "Tarikh": datetime.today().strftime('%Y-%m-%d'), "Kawasan": kawasan,
                    "Kategori": hasil_ai.get("kategori", "Sisa Campuran"), "Risiko": hasil_ai.get("risiko", "Sederhana"),
                    "Lat": st.session_state.click_coord[0], "Lon": st.session_state.click_coord[1], "Status": "Baru",
                    "Nama": nama_input, "Telefon": tel_input, "Emel": emel_input if emel_input else "Tiada",
                    "Catatan": catatan_input if catatan_input else "Tiada catatan."
                }
                st.session_state.db_aduan.append(rekod)
                st.success(f"🎉 Aduan {id_baru} berjaya dihantar ke {kawasan}.")
                st.rerun()

# ------------------------------------------
# MOD 3: DASHBOARD ADMIN PBT (PREMIUM CARDS RESTORED)
# ------------------------------------------
elif mode == "🏢 Login PBT Admin":
    if not st.session_state.auth["logged_in"]:
        st.title("🔐 Log Masuk Pegawai PBT")
        with st.form("login_form"):
            user_input = st.text_input("ID Pengguna PBT:")
            pass_input = st.text_input("Kata Laluan:", type="password")
            submit_login = st.form_submit_button("Masuk")
            if submit_login and user_input in USERS_PBT and USERS_PBT[user_input]["pass"] == pass_input:
                st.session_state.auth = {"logged_in": True, "user": user_input, "pbt_name": USERS_PBT[user_input]["nama"]}
                st.rerun()
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
        st.subheader("📋 Senarai Aduan & Profil Tindakan Lapangan")
        
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
                        if aduan['Risiko'] == "Tinggi": st.error(f"🚨 **Risiko:** {aduan['Risiko']}")
                        else: st.warning(f"⚠️ **Risiko:** {aduan['Risiko']}")
                        st.write(f"📍 **Koordinat:** `{aduan['Lat']:.4f}, {aduan['Lon']:.4f}`")
                    with col_pengadu:
                        st.markdown("🗣️ **Maklumat Pengadu:**")
                        st.write(f"👤 **Nama:** {aduan.get('Nama', 'Anonym')}")
                        st.write(f"📞 **No. Tel:** {aduan.get('Telefon', 'Tiada')}")
                        st.info(f"💬 **Catatan:** {aduan.get('Catatan', 'Tiada')}")
                    with col_img:
                        st.markdown("**📸 Gambar Bukti:**")
                        st.image("https://images.unsplash.com/photo-1611284446314-60a58ac0deb9?w=400", width=180)
                    with col_action:
                        st.markdown("**⚡ Status:**")
                        status_baru = st.selectbox("Tukar:", ["Baru", "Dalam Tindakan", "Selesai"], key=f"sel_{aduan['ID']}", index=["Baru", "Dalam Tindakan", "Selesai"].index(aduan['Status']))
                        if st.button("Simpan", key=f"btn_{aduan['ID']}"):
                            for main_r in st.session_state.db_aduan:
                                if main_r["ID"] == aduan['ID']: main_r["Status"] = status_baru
                            st.success("Dikemaskini!")
                            st.rerun()
                st.markdown("<hr style='border:1px dashed #ccc'>", unsafe_allow_html=True)