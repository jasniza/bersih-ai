else:
        pbt_full_name = st.session_state.auth['pbt_name']
        daerah_tapis = pbt_full_name.replace("MB ", "").replace("MP ", "").replace("MD ", "")
        
        st.title(f"🏢 Dashboard Operasi {pbt_full_name}")
        st.subheader(f"Pengurusan Sisa Haram Daerah {daerah_tapis}")
        
        # Ambil data aduan daerah berkenaan sahaja
        data_daerah_sahaja = [r for r in st.session_state.db_aduan if r["Kawasan"] == daerah_tapis]
        
        # KPI RINGKAS DAERAH
        col1, col2, col3 = st.columns(3)
        col1.metric(f"Jumlah Aduan {daerah_tapis}", len(data_daerah_sahaja))
        col2.metric("Kes Baru", len([r for r in data_daerah_sahaja if r["Status"]=="Baru"]))
        col3.metric("Selesai", len([r for r in data_daerah_sahaja if r["Status"]=="Selesai"]))
        
        st.markdown("---")
        st.subheader("📋 Senarai Aduan & Profil Tindakan Lapangan")
        
        if not data_daerah_sahaja:
            st.info(f"Alhamdulillah, tiada aduan aktif di daerah {daerah_tapis} buat masa ini.")
        else:
            # Bina kad tindakan dinamik untuk setiap aduan (Bukan st.table kaku lagi)
            for aduan in data_daerah_sahaja:
                with st.container():
                    col_info, col_pengadu, col_img, col_action = st.columns([2, 2, 2, 1])
                    
                    # 1. Kolum Info Aduan & AI
                    with col_info:
                        st.markdown(f"### 🆔 {aduan['ID']}")
                        st.write(f"📅 **Tarikh Lapor:** {aduan['Tarikh']}")
                        st.write(f"🚯 **Kategori AI:** {aduan['Kategori']}")
                        if aduan['Risiko'] == "Tinggi": 
                            st.error(f"🚨 **Risiko:** {aduan['Risiko']}")
                        elif aduan['Risiko'] == "Sederhana":
                            st.warning(f"⚠️ **Risiko:** {aduan['Risiko']}")
                        else: 
                            st.success(f"✅ **Risiko:** {aduan['Risiko']}")
                        st.write(f"📍 **Koordinat:** `{aduan['Lat']:.4f}, {aduan['Lon']:.4f}`")
                    
                    # 2. Kolum Maklumat Pengadu
                    with col_pengadu:
                        st.markdown("🗣️ **Maklumat Pengadu:**")
                        st.write(f"👤 **Nama:** {aduan.get('Nama', 'Anonim')}")
                        st.write(f"📞 **No. Tel:** {aduan.get('Telefon', 'Tiada')}")
                        st.write(f"✉️ **Emel:** {aduan.get('Emel', 'Tiada')}")
                        st.info(f"💬 **Catatan:** {aduan.get('Catatan', 'Tiada')}")
                    
                    # 3. Kolum Gambar Bukti Lapangan
                    with col_img:
                        st.markdown("**📸 Gambar Bukti:**")
                        if aduan['ID'] in ["ADU-001", "ADU-002", "ADU-003", "ADU-004"]:
                            st.image("https://images.unsplash.com/photo-1611284446314-60a58ac0deb9?w=400", width=180, caption="Bukti Lokasi")
                        else:
                            st.info("🖼️ Gambar sedia pada pelayan.")
                    
                    # 4. Kolum Borang Kemas Kini Status Operasi PBT
                    with col_action:
                        st.markdown("**⚡ Status Tindakan:**")
                        # Papar label status semasa
                        status_semasa = aduan['Status']
                        status_warna = "🔵 Baru" if status_semasa == "Baru" else "🟡 Dalam Tindakan" if status_semasa == "Dalam Tindakan" else "🟢 Selesai"
                        st.markdown(f"**Semasa:** {status_warna}")
                        
                        # Kotak pilihan untuk menukar status lori
                        senarai_pilihan = ["Baru", "Dalam Tindakan", "Selesai"]
                        indeks_asal = senarai_pilihan.index(status_semasa) if status_semasa in senarai_pilihan else 0
                        
                        status_baru = st.selectbox("Tukar Ke:", senarai_pilihan, key=f"sel_{aduan['ID']}", index=indeks_asal)
                        
                        # Butang untuk simpan perubahan ke database session_state
                        if st.button("Simpan 💾", key=f"btn_{aduan['ID']}"):
                            for main_r in st.session_state.db_aduan:
                                if main_r["ID"] == aduan['ID']: 
                                    main_r["Status"] = status_baru
                            st.success(f"ID {aduan['ID']} Dikemaskini!")
                            st.rerun()
                            
                # Garis pemisah antara aduan
                st.markdown("<hr style='border:1px dashed #ccc'>", unsafe_allow_html=True)