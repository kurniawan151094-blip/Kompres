import streamlit as st
import io
import zipfile
from PIL import Image
from pypdf import PdfReader, PdfWriter

st.set_page_config(
    page_title="Universal File Compressor",
    page_icon="🗜️",
    layout="centered"
)

st.title("🗜️ Universal File Compressor")
st.write("Perkecil ukuran file **Gambar (JPG/PNG)**, **Dokumen PDF**, serta **Office (Word, Excel, PowerPoint)**.")

# ================= FUNGSI BANTUAN KOMPRESI OFFICE =================
def compress_office_file(file_bytes, image_quality=60):
    in_buf = io.BytesIO(file_bytes)
    out_buf = io.BytesIO()
    
    with zipfile.ZipFile(in_buf, 'r') as in_zip:
        with zipfile.ZipFile(out_buf, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as out_zip:
            for item in in_zip.infolist():
                content = in_zip.read(item.filename)
                
                # Cek jika ada file gambar internal di dokumen (biasanya di folder media/)
                if any(item.filename.lower().endswith(ext) for ext in ('.png', '.jpg', '.jpeg')) and 'media/' in item.filename:
                    try:
                        img = Image.open(io.BytesIO(content))
                        img_buf = io.BytesIO()
                        
                        if item.filename.lower().endswith(('.jpg', '.jpeg')):
                            if img.mode in ("RGBA", "P"):
                                img = img.convert("RGB")
                            img.save(img_buf, format="JPEG", quality=image_quality, optimize=True)
                        elif item.filename.lower().endswith('.png'):
                            img.save(img_buf, format="PNG", optimize=True)
                            
                        compressed_img = img_buf.getvalue()
                        # Pakai gambar baru jika ukurannya terbukti lebih kecil
                        if len(compressed_img) < len(content):
                            content = compressed_img
                    except Exception:
                        pass
                
                out_zip.writestr(item, content)
                
    return out_buf.getvalue()

# ================= MEMBUAT TABS =================
tab_img, tab_pdf, tab_office = st.tabs([
    "🖼️ Gambar (JPG/PNG)", 
    "📄 Dokumen PDF", 
    "📊 Office (Word, Excel, PPT)"
])

# ================= 1. TAB GAMBAR (INTERAKTIF & REAL-TIME) =================
with tab_img:
    st.subheader("Kompres Gambar Cerdas (Live Preview)")
    file_img = st.file_uploader("Upload gambar Anda", type=["jpg", "jpeg", "png", "webp"], key="upload_img")
    
    if file_img:
        img_original = Image.open(file_img)
        size_awal_kb = len(file_img.getvalue()) / 1024
        
        st.write("---")
        # Kontrol Slider
        col_ctrl1, col_ctrl2 = st.columns(2)
        with col_ctrl1:
            quality = st.slider("🎚️ Kualitas Gambar (%)", min_value=10, max_value=95, value=70)
        with col_ctrl2:
            scale = st.slider("📐 Skala Dimensi (%)", min_value=10, max_value=100, value=100)

        # Proses otomatis di memori setiap kali slider bergeser
        img_proses = img_original.copy()
        new_w = int(img_original.width * (scale / 100))
        new_h = int(img_original.height * (scale / 100))
        
        if scale < 100:
            img_proses = img_proses.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
        out_img = io.BytesIO()
        if img_proses.mode in ("RGBA", "P"):
            img_proses = img_proses.convert("RGB")
            
        img_proses.save(out_img, format="JPEG", quality=quality, optimize=True)
        res_img_bytes = out_img.getvalue()
        
        size_akhir_kb = len(res_img_bytes) / 1024
        hemat_img = ((size_awal_kb - size_akhir_kb) / size_awal_kb) * 100
        
        # Ringkasan Informasi Live
        st.write("---")
        m1, m2, m3 = st.columns(3)
        m1.metric(label="Ukuran Asli", value=f"{size_awal_kb:.1f} KB")
        m2.metric(
            label="Estimasi Hasil", 
            value=f"{size_akhir_kb:.1f} KB", 
            delta=f"-{hemat_img:.1f}%", 
            delta_color="normal"
        )
        m3.metric(label="Resolusi Piksel", value=f"{new_w} × {new_h} px")

        # Tombol Download Terintegrasi
        st.download_button(
            label=f"⬇️ Download Hasil Kompresi ({size_akhir_kb:.1f} KB)",
            data=res_img_bytes,
            file_name=f"compressed_{file_img.name.rsplit('.', 1)[0]}.jpg",
            mime="image/jpeg",
            use_container_width=True
        )

        # Layar Komparasi Gambar (Asli vs Hasil)
        st.write("---")
        st.caption("🔍 Periksa ketajaman gambar di bawah ini sebelum mendownload:")
        prev1, prev2 = st.columns(2)
        with prev1:
            st.image(file_img, caption=f"Asli ({img_original.width}×{img_original.height})", use_container_width=True)
        with prev2:
            st.image(res_img_bytes, caption=f"Hasil Kompresi ({new_w}×{new_h})", use_container_width=True)

# ================= 2. TAB PDF =================
with tab_pdf:
    st.subheader("Kompres Dokumen PDF")
    file_pdf = st.file_uploader("Upload Dokumen PDF", type=["pdf"], key="upload_pdf")
    
    if file_pdf:
        size_awal_pdf = len(file_pdf.getvalue()) / 1024
        st.info(f"Ukuran Asli Dokumen: **{size_awal_pdf:.2f} KB**")
        
        if st.button("🚀 Mulai Kompres Dokumen PDF", key="btn_pdf", use_container_width=True):
            with st.spinner("Sedang memproses struktur dokumen PDF..."):
                reader = PdfReader(file_pdf)
                writer = PdfWriter()
                
                for page in reader.pages:
                    page.compress_content_streams()
                    writer.add_page(page)
                    
                out_pdf = io.BytesIO()
                writer.write(out_pdf)
                res_pdf_bytes = out_pdf.getvalue()
                
                size_akhir_pdf = len(res_pdf_bytes) / 1024
                hemat_pdf = ((size_awal_pdf - size_akhir_pdf) / size_awal_pdf) * 100 if size_awal_pdf > 0 else 0
                
                st.success(f"Ukuran Baru: **{size_akhir_pdf:.2f} KB** (Hemat {hemat_pdf:.1f}%)")
                st.download_button(
                    label="⬇️ Download PDF Hasil Kompresi",
                    data=res_pdf_bytes,
                    file_name=f"compressed_{file_pdf.name}",
                    mime="application/pdf",
                    use_container_width=True
                )

# ================= 3. TAB OFFICE (DOCX, PPTX, XLSX) =================
with tab_office:
    st.subheader("Kompres File Word, PowerPoint, & Excel")
    st.caption("Aplikasi akan memadatkan arsip dokumen dan memperkecil resolusi foto/gambar internal yang menempel di dalamnya.")
    
    file_office = st.file_uploader("Upload File Office (.docx, .pptx, .xlsx)", type=["docx", "pptx", "xlsx"], key="upload_office")
    
    if file_office:
        size_awal_off = len(file_office.getvalue()) / 1024
        st.info(f"Ukuran Asli Dokumen: **{size_awal_off:.2f} KB**")
        
        img_q = st.slider("Kualitas Gambar di Dalam Dokumen (%)", min_value=20, max_value=90, value=60, help="Makin rendah persentasenya, gambar di dalam slide/dokumen makin hemat ukuran.")
        
        if st.button("🚀 Mulai Optimasi Dokumen Office", key="btn_office", use_container_width=True):
            with st.spinner("Sedang mengoptimasi dan mengompres dokumen..."):
                res_off_bytes = compress_office_file(file_office.getvalue(), image_quality=img_q)
                size_akhir_off = len(res_off_bytes) / 1024
                hemat_off = ((size_awal_off - size_akhir_off) / size_awal_off) * 100 if size_awal_off > 0 else 0
                
                st.success(f"Ukuran Baru: **{size_akhir_off:.2f} KB** (Hemat {hemat_off:.1f}%)")
                st.download_button(
                    label=f"⬇️ Download File Hasil Optimasi ({size_akhir_off:.1f} KB)",
                    data=res_off_bytes,
                    file_name=f"optimized_{file_office.name}",
                    mime="application/octet-stream",
                    use_container_width=True
                )
