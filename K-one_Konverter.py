import streamlit as st
import io
import zipfile
from PIL import Image
from pypdf import PdfReader, PdfWriter

st.set_page_config(page_title="Document & Image Compressor", page_icon="🗜️", layout="centered")

st.title("🗜️ Document & Image Compressor")
st.write("Kompres file **Gambar (JPG/PNG)**, **PDF**, dan **Dokumen Office (Word, Excel, PowerPoint)**.")

# Fungsi kompresi cerdas untuk Office (Word, Excel, PPT)
def compress_office_file(file_bytes, image_quality=60):
    in_buf = io.BytesIO(file_bytes)
    out_buf = io.BytesIO()
    
    with zipfile.ZipFile(in_buf, 'r') as in_zip:
        with zipfile.ZipFile(out_buf, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as out_zip:
            for item in in_zip.infolist():
                content = in_zip.read(item.filename)
                
                # Cek jika ada file gambar di dalam folder media Word/PPT/Excel
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
                        # Gunakan gambar hasil kompresi jika ukurannya lebih kecil dari aslinya
                        if len(compressed_img) < len(content):
                            content = compressed_img
                    except Exception:
                        pass
                
                out_zip.writestr(item, content)
                
    return out_buf.getvalue()

# Tab Pilihan
tab_img, tab_pdf, tab_office = st.tabs([
    "🖼️ Gambar (JPG/PNG)", 
    "📄 Dokumen PDF", 
    "📊 Office (Word, Excel, PPT)"
])

# ================= 1. TAB GAMBAR =================
with tab_img:
    st.subheader("Kompres File Gambar")
    file_img = st.file_uploader("Pilih file JPG atau PNG", type=["jpg", "jpeg", "png"], key="upload_img")
    
    if file_img:
        size_awal = len(file_img.getvalue()) / 1024
        st.info(f"Ukuran Asli: **{size_awal:.2f} KB**")
        
        quality = st.slider("Kualitas Gambar (%)", min_value=10, max_value=95, value=70)
        scale = st.slider("Skala Dimensi (%)", min_value=20, max_value=100, value=100, help="Turunkan jika ingin ukuran file jauh lebih kecil.")
        
        if st.button("🚀 Kompres Gambar", key="btn_img"):
            img = Image.open(file_img)
            
            # Ubah dimensi gambar jika skala di bawah 100%
            if scale < 100:
                new_w = int(img.width * (scale / 100))
                new_h = int(img.height * (scale / 100))
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                
            out = io.BytesIO()
            file_ext = file_img.name.rsplit('.', 1)[-1].lower()
            
            if file_ext in ['jpg', 'jpeg']:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(out, format="JPEG", quality=quality, optimize=True)
                mime_type = "image/jpeg"
            else:
                # Untuk PNG
                img.save(out, format="PNG", optimize=True)
                mime_type = "image/png"
                
            res_bytes = out.getvalue()
            size_akhir = len(res_bytes) / 1024
            hemat = ((size_awal - size_akhir) / size_awal) * 100 if size_awal > 0 else 0
            
            st.success(f"Ukuran Baru: **{size_akhir:.2f} KB** (Hemat {hemat:.1f}%)")
            st.download_button(
                label="⬇️ Download Gambar Hasil Kompresi",
                data=res_bytes,
                file_name=f"compressed_{file_img.name}",
                mime=mime_type
            )

# ================= 2. TAB PDF =================
with tab_pdf:
    st.subheader("Kompres Dokumen PDF")
    file_pdf = st.file_uploader("Pilih file PDF", type=["pdf"], key="upload_pdf")
    
    if file_pdf:
        size_awal = len(file_pdf.getvalue()) / 1024
        st.info(f"Ukuran Asli: **{size_awal:.2f} KB**")
        
        if st.button("🚀 Kompres Dokumen PDF", key="btn_pdf"):
            reader = PdfReader(file_pdf)
            writer = PdfWriter()
            
            for page in reader.pages:
                page.compress_content_streams()  # Mengompres teks & elemen visual PDF
                writer.add_page(page)
                
            out = io.BytesIO()
            writer.write(out)
            res_bytes = out.getvalue()
            size_akhir = len(res_bytes) / 1024
            hemat = ((size_awal - size_akhir) / size_awal) * 100 if size_awal > 0 else 0
            
            st.success(f"Ukuran Baru: **{size_akhir:.2f} KB** (Hemat {hemat:.1f}%)")
            st.download_button(
                label="⬇️ Download PDF Hasil Kompresi",
                data=res_bytes,
                file_name=f"compressed_{file_pdf.name}",
                mime="application/pdf"
            )

# ================= 3. TAB OFFICE (DOCX, PPTX, XLSX) =================
with tab_office:
    st.subheader("Kompres Dokumen Word, PowerPoint, & Excel")
    st.caption("Aplikasi akan memadatkan arsip dokumen dan memperkecil gambar internal di dalamnya.")
    
    file_office = st.file_uploader("Pilih file (.docx, .pptx, .xlsx)", type=["docx", "pptx", "xlsx"], key="upload_office")
    
    if file_office:
        size_awal = len(file_office.getvalue()) / 1024
        st.info(f"Ukuran Asli: **{size_awal:.2f} KB**")
        
        img_q = st.slider("Kualitas Gambar di Dalam Dokumen (%)", min_value=20, max_value=90, value=60)
        
        if st.button("🚀 Optimasi & Kompres Dokumen", key="btn_office"):
            with st.spinner("Sedang memproses dan mengompres dokumen..."):
                res_bytes = compress_office_file(file_office.getvalue(), image_quality=img_q)
                size_akhir = len(res_bytes) / 1024
                hemat = ((size_awal - size_akhir) / size_awal) * 100 if size_awal > 0 else 0
                
                st.success(f"Ukuran Baru: **{size_akhir:.2f} KB** (Hemat {hemat:.1f}%)")
                st.download_button(
                    label="⬇️ Download Dokumen Hasil Kompresi",
                    data=res_bytes,
                    file_name=f"optimized_{file_office.name}",
                    mime="application/octet-stream"
                )
