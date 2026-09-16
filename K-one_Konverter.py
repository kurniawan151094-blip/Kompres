# ================= 1. TAB GAMBAR (INTERAKTIF & REAL-TIME) =================
with tab_img:
    st.subheader("Kompres Gambar Cerdas (Live Preview)")
    file_img = st.file_uploader("Pilih file JPG atau PNG", type=["jpg", "jpeg", "png", "webp"], key="upload_img")
    
    if file_img:
        # Buka gambar asli
        img_original = Image.open(file_img)
        size_awal_kb = len(file_img.getvalue()) / 1024
        
        st.write("---")
        # Kolom Pengaturan Slider
        col_ctrl1, col_ctrl2 = st.columns(2)
        with col_ctrl1:
            quality = st.slider("🎚️ Kualitas Gambar (%)", min_value=10, max_value=95, value=70)
        with col_ctrl2:
            scale = st.slider("📐 Skala Dimensi (%)", min_value=10, max_value=100, value=100)

        # PROSES REAL-TIME DI LATAR BELAKANG SETIAP SLIDER DIGESER
        img_proses = img_original.copy()
        
        # 1. Sesuaikan Dimensi
        new_w = int(img_original.width * (scale / 100))
        new_h = int(img_original.height * (scale / 100))
        if scale < 100:
            img_proses = img_proses.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
        # 2. Kompresi di memori
        out = io.BytesIO()
        if img_proses.mode in ("RGBA", "P"):
            img_proses = img_proses.convert("RGB")
            
        img_proses.save(out, format="JPEG", quality=quality, optimize=True)
        res_bytes = out.getvalue()
        
        # Hitung ukuran baru secara langsung
        size_akhir_kb = len(res_bytes) / 1024
        hemat = ((size_awal_kb - size_akhir_kb) / size_awal_kb) * 100
        
        # TAMPILAN INFORMASI REAL-TIME (METRICS)
        st.write("---")
        m1, m2, m3 = st.columns(3)
        m1.metric(label="Ukuran Awal", value=f"{size_awal_kb:.1f} KB")
        m2.metric(
            label="Estimasi Hasil Kompresi", 
            value=f"{size_akhir_kb:.1f} KB", 
            delta=f"-{hemat:.1f}%", 
            delta_color="normal"
        )
        m3.metric(label="Dimensi Baru", value=f"{new_w} × {new_h} px")

        # TOMBOL DOWNLOAD (Selalu update mengikuti posisi slider)
        st.download_button(
            label=f"⬇️ Download Gambar ({size_akhir_kb:.1f} KB)",
            data=res_bytes,
            file_name=f"compressed_{file_img.name.rsplit('.', 1)[0]}.jpg",
            mime="image/jpeg",
            use_container_width=True
        )

        # PREVIEW SEBELUM & SESUDAH
        st.write("---")
        st.caption("🔍 Cek apakah gambar pecah sebelum Anda mengunduhnya:")
        prev1, prev2 = st.columns(2)
        with prev1:
            st.image(file_img, caption=f"Asli ({img_original.width}×{img_original.height})", use_container_width=True)
        with prev2:
            st.image(res_bytes, caption=f"Hasil Kompresi ({new_w}×{new_h})", use_container_width=True)
