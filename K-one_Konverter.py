import streamlit as st
import io
import time
import zipfile
import streamlit.components.v1 as components
from PIL import Image
from pypdf import PdfReader, PdfWriter

# Konfigurasi Halaman (Sidebar tertutup secara default)
st.set_page_config(
    page_title="CompressPro",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* 1. KURANGI JARAK KOSONG DI ATAS */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0px !important;
    }
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 680px;
    }

    /* 2. IKON HAMBURGER KIRI ATAS DIBUAT BESAR & JELAS */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        position: fixed !important;
        top: 12px !important;
        left: 12px !important;
        z-index: 999999 !important;
    }

    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"] button {
        width: 52px !important;
        height: 52px !important;
        background-color: #2563EB !important;
        border-radius: 14px !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.45) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg {
        width: 30px !important;
        height: 30px !important;
        stroke: #ffffff !important;
        fill: #ffffff !important;
        color: #ffffff !important;
    }

    /* 3. TOMBOL-TOMBOL DI DALAM SIDEBAR DIBUAT BESAR */
    [data-testid="stSidebar"] .stButton > button {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        padding: 0.95rem 1.2rem !important;
        margin-bottom: 0.7rem !important;
        border-radius: 12px !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }

    /* 4. HEADER UTAMA */
    .brand-header {
        text-align: center;
        margin-top: 0.2rem;
        margin-bottom: 1.2rem;
    }
    .brand-title {
        font-size: 1.75rem;
        font-weight: 800;
        background: linear-gradient(90deg, #2563EB, #7C3AED);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .brand-sub {
        font-size: 0.9rem;
        color: #64748B;
        font-weight: 600;
        margin-top: 3px;
    }

    /* 5. KARTU METRIK RESPONSIF HP */
    .metrics-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 6px;
        margin: 1rem 0;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 8px 6px;
        text-align: center;
    }
    .metric-card.highlight {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
    }
    .metric-label {
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #64748B;
    }
    .metric-value {
        font-size: 0.95rem;
        font-weight: 800;
        color: #0F172A;
        margin-top: 2px;
    }
    .metric-card.highlight .metric-value {
        color: #1D4ED8;
    }
    .badge-hemat {
        display: inline-block;
        background: #DCFCE7;
        color: #15803D;
        font-size: 0.68rem;
        font-weight: 700;
        padding: 2px 5px;
        border-radius: 999px;
        margin-top: 2px;
    }

    /* 6. INFO TIP */
    .info-tip {
        background: #F8FAFC;
        border-left: 3px solid #3B82F6;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 0.82rem;
        color: #475569;
        margin: 1rem 0 0.6rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi State
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "🖼️ Kompres Gambar"

if "close_sidebar_trigger" not in st.session_state:
    st.session_state.close_sidebar_trigger = False

# ================= SKRIP PENUTUP OTOMATIS SIDEBAR =================
if st.session_state.close_sidebar_trigger:
    st.session_state.close_sidebar_trigger = False
    # Menggunakan timestamp unik agar script selalu dieksekusi setiap tombol diklik
    components.html(f"""
        <script>
            // Timestamp: {time.time()}
            setTimeout(function() {{
                try {{
                    const parentDoc = window.parent.document;
                    const closeBtn = parentDoc.querySelector('[data-testid="stSidebarCollapseButton"] button') ||
                                     parentDoc.querySelector('button[aria-label="Close sidebar"]') ||
                                     parentDoc.querySelector('[data-testid="stSidebarCollapseButton"]');
                    if (closeBtn) {{
                        closeBtn.click();
                    }} else {{
                        const backdrop = parentDoc.querySelector('[data-testid="stSidebarBackdrop"]');
                        if (backdrop) backdrop.click();
                    }}
                }} catch (e) {{
                    console.log(e);
                }}
            }}, 50);
        </script>
    """, height=0, width=0)

# ================= MENU DI DALAM SIDEBAR =================
with st.sidebar:
    st.markdown("<h2 style='font-weight:800; color:#0F172A; margin-top:0;'>⚡ Menu Pilihan</h2>", unsafe_allow_html=True)
    st.write("")
    
    daftar_menu = [
        ("🖼️ Kompres Gambar", "btn_nav_img"),
        ("📄 Kompres Dokumen PDF", "btn_nav_pdf"),
        ("📊 Kompres Dokumen Office", "btn_nav_office")
    ]
    
    for label, key_btn in daftar_menu:
        is_active = (st.session_state.active_menu == label)
        tipe_tombol = "primary" if is_active else "secondary"
        
        if st.button(label, key=key_btn, use_container_width=True, type=tipe_tombol):
            st.session_state.active_menu = label
            st.session_state.close_sidebar_trigger = True
            st.rerun()

# ================= HEADER UTAMA =================
st.markdown(f"""
<div class="brand-header">
    <h1 class="brand-title">⚡ CompressPro</h1>
    <div class="brand-sub">{st.session_state.active_menu}</div>
</div>
""", unsafe_allow_html=True)

# ================= FUNGSI BANTUAN KOMPRESI OFFICE =================
def compress_office_file(file_bytes, image_quality=60):
    in_buf = io.BytesIO(file_bytes)
    out_buf = io.BytesIO()
    
    with zipfile.ZipFile(in_buf, 'r') as in_zip:
        with zipfile.ZipFile(out_buf, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as out_zip:
            for item in in_zip.infolist():
                content = in_zip.read(item.filename)
                
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


# ================= 1. HALAMAN KOMPRES GAMBAR =================
if st.session_state.active_menu == "🖼️ Kompres Gambar":
    file_img = st.file_uploader("Upload Foto / Gambar (JPG, PNG)", type=["jpg", "jpeg", "png", "webp"])
    
    if file_img:
        img_original = Image.open(file_img)
        size_awal_kb = len(file_img.getvalue()) / 1024
        
        col1, col2 = st.columns(2)
        with col1:
            quality = st.slider("Kualitas Kompresi", 10, 95, 70)
        with col2:
            scale = st.slider("Skala Resolusi (%)", 10, 100, 100)

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

        st.download_button(
            label=f"⬇️ Download Gambar ({size_akhir_kb:.1f} KB)",
            data=res_img_bytes,
            file_name=f"compressed_{file_img.name.rsplit('.', 1)[0]}.jpg",
            mime="image/jpeg",
            use_container_width=True
        )

        st.markdown("""
        <div class="info-tip">
            🔍 <b>Pratinjau:</b> Geser tab di bawah untuk melihat ketajaman gambar:
        </div>
        """, unsafe_allow_html=True)

        tab_hasil, tab_asli = st.tabs(["✨ Hasil Baru", "🔍 Foto Asli"])
        with tab_hasil:
            st.image(res_img_bytes, caption=f"Hasil Baru ({new_w} × {new_h} px)", use_container_width=True)
        with tab_asli:
            st.image(file_img, caption=f"Foto Asli ({img_original.width} × {img_original.height} px)", use_container_width=True)


# ================= 2. HALAMAN KOMPRES PDF =================
elif st.session_state.active_menu == "📄 Kompres Dokumen PDF":
    file_pdf = st.file_uploader("Upload Dokumen PDF", type=["pdf"])
    
    if file_pdf:
        size_awal_pdf = len(file_pdf.getvalue()) / 1024
        st.info(f"Ukuran Asli Dokumen: **{size_awal_pdf:.2f} KB**")
        
        if st.button("🚀 Mulai Kompres Dokumen PDF", use_container_width=True):
            with st.spinner("Mengompres file PDF..."):
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


# ================= 3. HALAMAN KOMPRES OFFICE =================
elif st.session_state.active_menu == "📊 Kompres Dokumen Office":
    st.caption("Mendukung Word (.docx), PowerPoint (.pptx), dan Excel (.xlsx)")
    file_office = st.file_uploader("Upload Dokumen Office", type=["docx", "pptx", "xlsx"])
    
    if file_office:
        size_awal_off = len(file_office.getvalue()) / 1024
        st.info(f"Ukuran Asli Dokumen: **{size_awal_off:.2f} KB**")
        
        img_q = st.slider("Kualitas Kompresi Gambar Internal (%)", 20, 90, 60)
        
        if st.button("🚀 Mulai Kompres Dokumen Office", use_container_width=True):
            with st.spinner("Mengompres dokumen..."):
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
                    label=f"⬇️ Download Dokumen ({size_akhir_off:.1f} KB)",
                    data=res_off_bytes,
                    file_name=f"optimized_{file_office.name}",
                    mime="application/octet-stream",
                    use_container_width=True
                )
