import streamlit as st
import io
import zipfile
from PIL import Image
from pypdf import PdfReader, PdfWriter

# Konfigurasi Halaman
st.set_page_config(
    page_title="CompressPro - File Optimizer",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"  # Otomatis rapi saat pertama kali dibuka di HP
)

# ================= CUSTOM CSS (TAMPILAN MODERN & MOBILE-FRIENDLY) =================
st.markdown("""
<style>
    /* Font & Global Styling */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Header Modern */
    .main-header {
        text-align: center;
        padding: 1rem 0 1.5rem 0;
    }
    .main-header h1 {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #2563EB, #7C3AED);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }
    .main-header p {
        font-size: 0.95rem;
        color: #64748B;
        margin: 0;
    }

    /* Container Kartu Statistik (Metrics) Responsif untuk Layar HP */
    .metrics-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 10px 8px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    
    .metric-card.highlight {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
    }
    
    .metric-label {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748B;
        margin-bottom: 2px;
    }
    
    .metric-value {
        font-size: 1rem;
        font-weight: 700;
        color: #0F172A;
    }
    
    .metric-card.highlight .metric-value {
        color: #1D4ED8;
    }

    .badge-hemat {
        display: inline-block;
        background: #DCFCE7;
        color: #15803D;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 2px 6px;
        border-radius: 9999px;
        margin-top: 3px;
    }

    /* Kotak Info Tip */
    .info-tip {
        background: #F1F5F9;
        border-left: 4px solid #3B82F6;
        padding: 10px 14px;
        border-radius: 6px;
        font-size: 0.85rem;
        color: #334155;
        margin: 1.2rem 0 0.8rem 0;
    }

    /* Styling Slider & Tombol */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.55rem 1rem;
        transition: all 0.2s ease;
    }

    /* Penyesuaian Khusus Layar HP (Mobile) */
    @media (max-width: 640px) {
        .main-header h1 {
            font-size: 1.6rem;
        }
        .metrics-container {
            grid-template-columns: repeat(3, 1fr);
            gap: 6px;
        }
        .metric-value {
            font-size: 0.88rem;
        }
        .metric-label {
            font-size: 0.65rem;
        }
        .info-tip {
            font-size: 0.78rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ================= LOGIKA KOMPRESI OFFICE =================
def compress_office_file(file_bytes, image_quality=60):
    in_buf = io.BytesIO(file_bytes)
    out_buf = io.BytesIO()
    
    with zipfile.ZipFile(in_buf, 'r') as in_zip:
        with zipfile.ZipFile(out_buf, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as out_zip:
            for item in in_zip.infolist():
                content = in_zip.read(item.filename)
                
                # Optimasi gambar di dalam arsip dokumen
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
                        if len(compressed_img) < len(content):
                            content = compressed_img
                    except Exception:
                        pass
                
                out_zip.writestr(item, content)
                
    return out_buf.getvalue()

# ================= SIDEBAR MENU (HAMBURGER DRAWER DI HP) =================
with st.sidebar:
    st.markdown("### ⚡ **Menu Kompresi**")
    st.caption("Pilih jenis dokumen yang ingin Anda perkecil:")
    menu = st.radio(
        "Navigasi",
        options=["🖼️ Kompres Gambar", "📄 Kompres Dokumen PDF", "📊 Kompres Dokumen Office"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown(
        """
        <div style='font-size: 0.8rem; color: #64748B;'>
            🔒 <b>Aman & Privat:</b><br>
            File diproses langsung di memori dan tidak disimpan di server.
        </div>
        """, 
        unsafe_allow_html=True
    )

# ================= HEADER UTAMA =================
st.markdown("""
<div class="main-header">
    <h1>CompressPro</h1>
    <p>Optimasi file besar menjadi ringan dalam hitungan detik</p>
</div>
""", unsafe_allow_html=True)

# ================= 1. MENU GAMBAR =================
if menu == "🖼️ Kompres Gambar":
    file_img = st.file_uploader("Upload Foto / Gambar (JPG, PNG, WebP)", type=["jpg", "jpeg", "png", "webp"])
    
    if file_img:
        img_original = Image.open(file_img)
        size_awal_kb = len(file_img.getvalue()) / 1024
        
        # Pengaturan Slider
        col1, col2 = st.columns(2)
        with col1:
            quality = st.slider("Kualitas Kompresi", 10, 95, 70, help="Makin tinggi makin jernih.")
        with col2:
            scale = st.slider("Skala Dimensi (%)", 10, 100, 100, help="Turunkan skala jika file masih terlalu besar.")

        # Proses Real-time
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
        hemat = ((size_awal_kb - size_akhir_kb) / size_awal_kb) * 100
        
        # TAMPILAN METRIK KARTU PROFESIONAL (RESPONSIF HP)
        st.markdown(f"""
        <div class="metrics-container">
            <div class="metric-card">
                <div class="metric-label">Ukuran Asli</div>
                <div class="metric-value">{size_awal_kb:.1f} KB</div>
            </div>
            <div class="metric-card highlight">
                <div class="metric-label">Hasil Baru</div>
                <div class="metric-value">{size_akhir_kb:.1f} KB</div>
                <span class="badge-hemat">Hemat {hemat:.1f}%</span>
            </div>
            <div class="metric-card">
                <div class="metric-label">Resolusi</div>
                <div class="metric-value">{new_w}×{new_h}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Tombol Unduh Utama
        st.download_button(
            label=f"⬇️ Download Gambar ({size_akhir_kb:.1f} KB)",
            data=res_img_bytes,
            file_name=f"compressed_{file_img.name.rsplit('.', 1)[0]}.jpg",
            mime="image/jpeg",
            use_container_width=True
        )

        # Banner Info Rapi
        st.markdown("""
        <div class="info-tip">
            🔍 <b>Cek Pratinjau:</b> Geser tab di bawah untuk melihat ketajaman gambar sebelum Anda mengunduhnya.
        </div>
        """, unsafe_allow_html=True)

        # Tampilan Preview Tab (Ramah HP agar foto tidak terhimpit sempit)
        tab_hasil, tab_asli = st.tabs(["✨ Hasil Baru", "🔍 Gambar Asli"])
        with tab_hasil:
            st.image(res_img_bytes, caption=f"Hasil Kompresi ({new_w} × {new_h} px)", use_container_width=True)
        with tab_asli:
            st.image(file_img, caption=f"Asli ({img_original.width} × {img_original.height} px)", use_container_width=True)

# ================= 2. MENU DOKUMEN PDF =================
elif menu == "📄 Kompres Dokumen PDF":
    file_pdf = st.file_uploader("Upload Dokumen PDF", type=["pdf"])
    
    if file_pdf:
        size_awal_pdf = len(file_pdf.getvalue()) / 1024
        
        st.markdown(f"""
        <div class="metrics-container" style="grid-template-columns: 1fr;">
            <div class="metric-card">
                <div class="metric-label">Ukuran Asli PDF</div>
                <div class="metric-value">{size_awal_pdf:.2f} KB</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Mulai Kompres Dokumen PDF", use_container_width=True):
            with st.spinner("Sedang memproses struktur file PDF..."):
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
                
                st.markdown(f"""
                <div class="metrics-container" style="grid-template-columns: 1fr 1fr; margin-top: 1rem;">
                    <div class="metric-card">
                        <div class="metric-label">Ukuran Asli</div>
                        <div class="metric-value">{size_awal_pdf:.1f} KB</div>
                    </div>
                    <div class="metric-card highlight">
                        <div class="metric-label">Ukuran Baru</div>
                        <div class="metric-value">{size_akhir_pdf:.1f} KB</div>
                        <span class="badge-hemat">Hemat {hemat_pdf:.1f}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.download_button(
                    label="⬇️ Download PDF Hasil Kompresi",
                    data=res_pdf_bytes,
                    file_name=f"compressed_{file_pdf.name}",
                    mime="application/pdf",
                    use_container_width=True
                )

# ================= 3. MENU DOKUMEN OFFICE =================
elif menu == "📊 Kompres Dokumen Office":
    st.caption("Mendukung Word (.docx), PowerPoint (.pptx), dan Excel (.xlsx)")
    file_office = st.file_uploader("Upload Dokumen Office", type=["docx", "pptx", "xlsx"])
    
    if file_office:
        size_awal_off = len(file_office.getvalue()) / 1024
        
        st.markdown(f"""
        <div class="metrics-container" style="grid-template-columns: 1fr;">
            <div class="metric-card">
                <div class="metric-label">Ukuran Asli Dokumen</div>
                <div class="metric-value">{size_awal_off:.2f} KB</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        img_q = st.slider("Kualitas Gambar di Dalam Slide / Dokumen (%)", 20, 90, 60)
        
        if st.button("🚀 Mulai Kompres Dokumen Office", use_container_width=True):
            with st.spinner("Mengompres media dan memadatkan dokumen..."):
                res_off_bytes = compress_office_file(file_office.getvalue(), image_quality=img_q)
                size_akhir_off = len(res_off_bytes) / 1024
                hemat_off = ((size_awal_off - size_akhir_off) / size_awal_off) * 100 if size_awal_off > 0 else 0
                
                st.markdown(f"""
                <div class="metrics-container" style="grid-template-columns: 1fr 1fr; margin-top: 1rem;">
                    <div class="metric-card">
                        <div class="metric-label">Ukuran Asli</div>
                        <div class="metric-value">{size_awal_off:.1f} KB</div>
                    </div>
                    <div class="metric-card highlight">
                        <div class="metric-label">Ukuran Baru</div>
                        <div class="metric-value">{size_akhir_off:.1f} KB</div>
                        <span class="badge-hemat">Hemat {hemat_off:.1f}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.download_button(
                    label=f"⬇️ Download File ({size_akhir_off:.1f} KB)",
                    data=res_off_bytes,
                    file_name=f"optimized_{file_office.name}",
                    mime="application/octet-stream",
                    use_container_width=True
                )
