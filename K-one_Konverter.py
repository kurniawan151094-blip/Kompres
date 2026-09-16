import streamlit as st
import io
import os
import zipfile
import subprocess
import tempfile
from PIL import Image
from pypdf import PdfReader, PdfWriter

st.set_page_config(page_title="Universal File Compressor", page_icon="🗜️", layout="centered")

st.title("🗜️ Universal File Compressor")
st.write("Perkecil ukuran file Gambar, Dokumen PDF, Office, Video, atau buat Arsip ZIP.")

tab_img, tab_pdf, tab_office, tab_video, tab_zip = st.tabs([
    "🖼️ Gambar", "📄 PDF", "📊 Dokumen Office", "🎥 Video", "📦 Arsip ZIP"
])

# ================= 1. TAB GAMBAR =================
with tab_img:
    st.subheader("Kompres Gambar (JPG, PNG, WebP)")
    file_img = st.file_uploader("Upload Gambar", type=["jpg", "jpeg", "png", "webp"], key="img")
    
    if file_img:
        size_awal = len(file_img.getvalue()) / 1024
        st.write(f"Ukuran Asli: **{size_awal:.2f} KB**")
        
        quality = st.slider("Kualitas Kompresi (%)", 10, 95, 65, key="q_img")
        scale = st.slider("Ubah Skala Dimensi (%)", 10, 100, 100, key="scale_img")
        
        if st.button("Kompres Gambar", key="btn_img"):
            img = Image.open(file_img)
            
            # Ubah resolusi jika diminta
            if scale < 100:
                new_w = int(img.width * (scale / 100))
                new_h = int(img.height * (scale / 100))
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
                
            out = io.BytesIO()
            img.save(out, format="JPEG", quality=quality, optimize=True)
            res_bytes = out.getvalue()
            size_akhir = len(res_bytes) / 1024
            
            st.success(f"Ukuran Baru: **{size_akhir:.2f} KB** (Hemat {((size_awal - size_akhir)/size_awal)*100:.1f}%)")
            st.download_button("⬇️ Download Gambar", res_bytes, f"compressed_{file_img.name.rsplit('.', 1)[0]}.jpg", "image/jpeg")

# ================= 2. TAB PDF =================
with tab_pdf:
    st.subheader("Kompres Dokumen PDF")
    file_pdf = st.file_uploader("Upload Dokumen PDF", type=["pdf"], key="pdf")
    
    if file_pdf:
        size_awal = len(file_pdf.getvalue()) / 1024
        st.write(f"Ukuran Asli: **{size_awal:.2f} KB**")
        
        if st.button("Kompres Dokumen PDF", key="btn_pdf"):
            reader = PdfReader(file_pdf)
            writer = PdfWriter()
            
            for page in reader.pages:
                page.compress_content_streams()  # Mengompres teks & struktur internal
                writer.add_page(page)
                
            out = io.BytesIO()
            writer.write(out)
            res_bytes = out.getvalue()
            size_akhir = len(res_bytes) / 1024
            
            st.success(f"Ukuran Baru: **{size_akhir:.2f} KB** (Hemat {((size_awal - size_akhir)/size_awal)*100:.1f}%)")
            st.download_button("⬇️ Download PDF", res_bytes, f"compressed_{file_pdf.name}", "application/pdf")

# ================= 3. TAB OFFICE (DOCX, PPTX, XLSX) =================
with tab_office:
    st.subheader("Kompres Dokumen Office (Word, Excel, PowerPoint)")
    st.caption("File .docx/.xlsx/.pptx secara internal adalah arsip. Aplikasi akan memadatkannya kembali dengan kompresi tingkat maksimal (Deflate Level 9).")
    
    file_office = st.file_uploader("Upload Word / Excel / PowerPoint", type=["docx", "pptx", "xlsx"], key="office")
    
    if file_office:
        size_awal = len(file_office.getvalue()) / 1024
        st.write(f"Ukuran Asli: **{size_awal:.2f} KB**")
        
        if st.button("Optimasi Dokumen Office", key="btn_office"):
            in_zip = zipfile.ZipFile(file_office, 'r')
            out = io.BytesIO()
            
            with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as out_zip:
                for item in in_zip.infolist():
                    out_zip.writestr(item, in_zip.read(item.filename))
                    
            res_bytes = out.getvalue()
            size_akhir = len(res_bytes) / 1024
            
            st.success(f"Ukuran Baru: **{size_akhir:.2f} KB**")
            st.download_button("⬇️ Download Hasil Kompresi", res_bytes, f"optimized_{file_office.name}")

# ================= 4. TAB VIDEO =================
with tab_video:
    st.subheader("Kompres File Video (MP4)")
    st.caption("Memperkecil video membutuhkan waktu beberapa menit tergantung durasi video.")
    
    file_video = st.file_uploader("Upload Video", type=["mp4", "mov", "mkv"], key="video")
    
    if file_video:
        size_awal_mb = len(file_video.getvalue()) / (1024 * 1024)
        st.write(f"Ukuran Asli: **{size_awal_mb:.2f} MB**")
        
        crf = st.slider("Tingkat Kompresi Video (CRF)", 24, 35, 28, help="Makin tinggi angkanya, file makin kecil tapi kualitas berkurang.")
        
        if st.button("Kompres Video", key="btn_vid"):
            with st.spinner("Sedang memproses video dengan FFmpeg... Harap tunggu."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as in_tmp:
                    in_tmp.write(file_video.read())
                    in_path = in_tmp.name
                
                out_path = in_path.replace(".mp4", "_compressed.mp4")
                
                # Perintah FFmpeg H.264
                cmd = [
                    "ffmpeg", "-y", "-i", in_path,
                    "-vcodec", "libx264", "-crf", str(crf),
                    "-preset", "veryfast", "-acodec", "aac", out_path
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                if os.path.exists(out_path):
                    with open(out_path, "rb") as f:
                        res_bytes = f.read()
                    
                    size_akhir_mb = len(res_bytes) / (1024 * 1024)
                    st.success(f"Ukuran Baru: **{size_akhir_mb:.2f} MB** (Hemat {((size_awal_mb - size_akhir_mb)/size_awal_mb)*100:.1f}%)")
                    st.download_button("⬇️ Download Video", res_bytes, f"compressed_{file_video.name.rsplit('.', 1)[0]}.mp4", "video/mp4")
                    
                    # Bersihkan file sementara
                    os.remove(in_path)
                    os.remove(out_path)

# ================= 5. TAB ARSIP ZIP =================
with tab_zip:
    st.subheader("Kompres File Apapun Menjadi .ZIP")
    files = st.file_uploader("Upload satu atau banyak file", accept_multiple_files=True, key="multi_zip")
    
    if files:
        if st.button("Buat File ZIP", key="btn_zip"):
            out = io.BytesIO()
            with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_f:
                for f in files:
                    zip_f.writestr(f.name, f.read())
            
            res_bytes = out.getvalue()
            st.success("File ZIP berhasil dibuat!")
            st.download_button("⬇️ Download .ZIP", res_bytes, "arsip_terkompres.zip", "application/zip")