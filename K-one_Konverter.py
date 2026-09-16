import streamlit as st
import io
import zipfile
import streamlit.components.v1 as components
from PIL import Image
from pypdf import PdfReader, PdfWriter

# Konfigurasi Halaman (Default sidebar tertutup di awal)
st.set_page_config(
    page_title="CompressPro",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= CUSTOM CSS (MEMPERBESAR HAMBURGER & MENATA JARAK) =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* 1. KURANGI JARAK KOSONG ATAS */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    .main .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 680px;
    }

    /* 2. PERBESAR IKON HAMBURGER POJOK KIRI ATAS */
    [data-testid="collapsedControl"] {
        display: flex !important;
        position: fixed !important;
        top: 12px !important;
        left: 12px !important;
        z-index: 999999 !important;
    }
    [data-testid="collapsedControl"] button {
        width: 48px !important;
        height: 48px !important;
        background: #2563EB !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: transform 0.2s ease !important;
    }
    [data-testid="collapsedControl"] button:active {
        transform: scale(0.92) !important;
    }
    [data-testid="collapsedControl"] svg {
        width: 26px !important;
        height: 26px !important;
        stroke: white !important;
        fill: white !important;
    }

    /* 3. TOMBOL TUTUP DI DALAM LACI SIDEBAR */
    [data-testid="stSidebarCollapseButton"] button {
        width: 44px !important;
        height: 44px !important;
        border-radius: 10px !important;
        background: #F1F5F9 !important;
    }
    [data-testid="stSidebarCollapseButton"] svg {
        width: 22px !important;
        height: 22px !important;
    }

    /* 4. PERBESAR TOMBOL-TOMBOL DI DALAM SIDEBAR */
    [data-testid="stSidebar"] .stButton > button {
        height: auto !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        padding: 0.9rem 1.1rem !important;
        margin-bottom: 0.6rem !important;
        border-radius: 12px !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }

    /* 5. HEADER JUDUL APLIKASI */
    .brand-header {
        text-align: center;
        margin-top: 0.2rem;
        margin-bottom: 0.8rem;
    }
    .brand-title {
        font-size: 1.7rem;
        font-weight: 800;
        background: linear-gradient(90deg, #2563EB, #7C3AED);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .brand-sub {
        font-size: 0.85rem;
        color: #64748B;
        margin-top: 2px;
    }

    /* 6. INDIKATOR MODE AKTIF */
    .active-banner {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 8px 14px;
        margin-bottom: 1.2rem;
        font-size: 0.85rem;
        color: #334155;
    }

    /* 7. KARTU METRIK UKURAN FILE */
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

    /* 8. KOTAK TIP */
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

# Inisialisasi State Halaman
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "🖼️ Kompres Gambar"

if "trigger_close_sidebar" not in st.session_state:
    st.session_state.trigger_close_sidebar = False

# ================= KODE OTOMATIS PENUTUP SIDEBAR (BERGESER KEMBALI) =================
if st.session_state.trigger_close_sidebar:
    st.session_state.trigger_close_sidebar = False
    components.html("""
        <script>
            // Mencari tombol tutup di dalam laci sidebar dan menekannya otomatis
            var parentDoc = window.parent.document;
            var closeBtn = parentDoc.querySelector('[data-testid="stSidebarCollapseButton"] button') ||
                           parentDoc.querySelector('button[aria-label="Close sidebar"]');
            if (closeBtn) {
                closeBtn.click();
            }
        </script>
    """, height=0, width=0)

# ================= ISI LACI SIDEBAR =================
with st.sidebar:
    st.markdown("### ⚡ **Menu Kompresi**")
    st.caption("Pilih kategori di bawah ini:")
    
    menu_options = [
        ("🖼️ Kompres Gambar", "menu_img"),
        ("📄 Kompres Dokumen PDF", "menu_pdf"),
        ("📊 Kompres Dokumen Office", "menu_office")
    ]
    
    for label, key_name in menu_options:
        is_active = (st.session_state.active_menu == label)
        btn_type = "primary" if is_active else "secondary"
        
        if st.button(label, key=key_name, use_container_width=True, type=btn_type):
            st.session_state.active_menu = label
            # Aktifkan pemicu agar laci menutup otomatis
            st.session_state.trigger_close_sidebar = True
            st.rerun()

    st.markdown("---")
    st.markdown("""
        <div style='font-size: 0.78rem; color: #64748B;'>
            💡 <b>Tips:</b> Klik tombol menu di atas, maka laci sidebar akan otomatis bergeser menutup.
        </div>
    """, unsafe_allow_html=True)

# ================= HEADER UTAMA =================
st.markdown("""
<div class="brand-header">
    <h1 class="brand-title">⚡ CompressPro</h1>
    <div class="brand-sub">Kompres File Cepat & Berkualitas</div>
</div>
""", unsafe_allow_html=True)

# Indikator Mode Aktif
st.markdown(f"""
<div class="active-banner">
    <span>Kategori Terpilih: <b>{st.session_state.active_menu}</b></span>
    <span style="font-size: 0.75rem; color: #2563EB;">☰ Buka Menu di Kiri Atas</span>
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
    file_img = st.file_uploader("Upload Foto / Gambar", type=["jpg", "jpeg", "png", "webp"])
    
    if file_img:
        img_original = Image.open(file_img)
        size_awal_kb = len(file_img.getvalue()) / 1024
        
        col1, col2 = st.columns(2)
        with col1:
            quality = st.slider("Kualitas Kompresi", 10, 95, 70)
        with col2:
            scale = st.slider("Skala Resolusi (%)", 10, 100, 100)

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
        
        # Kartu Metrik Rapi di HP
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
            🔍 <b>Cek Pratinjau:</b> Pindah tab di bawah untuk melihat ketajaman gambar:
        </div>
        """, unsafe_allow_html=True)

        tab_hasil, tab_asli = st.tabs(["✨ Hasil Baru", "🔍 Foto Asli"])
        with tab_hasil:
            st.image(res_img_bytes, caption=f"Hasil Baru ({new_w} × {new_h} px)", use_container_width=True)
        with tab_asli:
            st.image(file_img, caption=f"Foto Asli ({img_original.width} × {img_original.height} px)", use_container_width=True)

# ================= 2. HALAMAN KOMPRES PDF =================
elif st.session_state.active_menu == "📄 Kompres Dokumen PDF":
    file_pdf = st.file_uploader("Upload File Dokumen PDF", type=["pdf"])
    
    if file_pdf:
        size_awal_pdf = len(file_pdf.getvalue()) / 1024
        st.info(f"Ukuran Asli Dokumen: **{size_awal_pdf:.2f} KB**")
        
        if st.button("🚀 Mulai Kompres Dokumen PDF", use_container_width=True):
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
    st.caption("Mendukung format Word (.docx), PowerPoint (.pptx), dan Excel (.xlsx)")
    file_office = st.file_uploader("Upload Dokumen Office", type=["docx", "pptx", "xlsx"])
    
    if file_office:
        size_awal_off = len(file_office.getvalue()) / 1024
        st.info(f"Ukuran Asli Dokumen: **{size_awal_off:.2f} KB**")
        
        img_q = st.slider("Kualitas Gambar di Dalam Dokumen (%)", 20, 90, 60)
        
        if st.button("🚀 Mulai Kompres Dokumen Office", use_container_width=True):
            with st.spinner("Mengompres dokumen dan media di dalamnya..."):
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
