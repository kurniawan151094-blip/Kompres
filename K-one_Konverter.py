import streamlit as st
import io
import time
import zipfile
import streamlit.components.v1 as components
from PIL import Image
from pypdf import PdfReader, PdfWriter

# Konfigurasi Halaman
st.set_page_config(
    page_title="CompressPro",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= CUSTOM CSS (RESPONSIF & MOBILE-FIRST) =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* 1. MENGHILANGKAN JARAK KOSONG DI ATAS */
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

    /* 2. IKON HAMBURGER BESAR & MENCOLOK DI KIRI ATAS */
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

    /* 3. TOMBOL SIDEBAR BESAR & RAMAH JARI */
    [data-testid="stSidebar"] .stButton > button {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        padding: 0.95rem 1.2rem !important;
        margin-bottom: 0.7rem !important;
        border-radius: 12px !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }

    /* 4. HEADER */
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

    /* 5. KARTU METRIK STATISTIK */
    .metrics-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin: 1.2rem 0;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 10px 6px;
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
        letter-spacing: 0.3px;
    }
    .metric-value {
        font-size: 0.98rem;
        font-weight: 800;
        color: #0F172A;
        margin-top: 3px;
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
        padding: 2px 6px;
        border-radius: 999px;
        margin-top: 3px;
    }

    /* 6. KOTAK TIP */
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

# Helper untuk format ukuran (B / KB / MB)
def format_size(size_in_bytes):
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    kb = size_in_bytes / 1024
    if kb >= 1024:
        return f"{kb / 1024:.2f} MB"
    return f"{kb:.2f} KB"

# Inisialisasi State Navigasi
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "🖼️ Kompres Gambar"

if "close_sidebar_trigger" not in st.session_state:
    st.session_state.close_sidebar_trigger = False

# ================= SKRIP OTOMATIS PENUTUP SIDEBAR =================
if st.session_state.close_sidebar_trigger:
    st.session_state.close_sidebar_trigger = False
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

# ================= MENU SIDEBAR =================
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


# ================= FUNGSI KOMPRESI OFFICE (DIPERBAIKI) =================
def compress_office_file(file_bytes, quality_slider=70):
    in_buf = io.BytesIO(file_bytes)
    out_buf = io.BytesIO()
    media_count = 0
    
    # 10% -> level 9 (maksimal), 95% -> level 1
    zip_level = max(1, min(9, int((100 - quality_slider) / 11) + 1))
    scale_factor = max(0.2, min(1.0, quality_slider / 100.0))
    
    with zipfile.ZipFile(in_buf, 'r') as in_zip:
        with zipfile.ZipFile(out_buf, 'w') as out_zip:
            for item in in_zip.infolist():
                content = in_zip.read(item.filename)
                fname_lower = item.filename.lower()
                
                is_img = any(fname_lower.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.webp'))
                is_media_folder = any(folder in fname_lower for folder in ('media/', 'pictures/'))
                
                if is_img and is_media_folder:
                    media_count += 1
                    try:
                        img = Image.open(io.BytesIO(content))
                        img_buf = io.BytesIO()
                        
                        # Turunkan dimensi gambar sesuai slider
                        new_w = max(1, int(img.width * scale_factor))
                        new_h = max(1, int(img.height * scale_factor))
                        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                        
                        if fname_lower.endswith(('.jpg', '.jpeg')):
                            if img_resized.mode in ("RGBA", "P"):
                                img_resized = img_resized.convert("RGB")
                            img_resized.save(img_buf, format="JPEG", quality=quality_slider, optimize=True)
                        elif fname_lower.endswith('.png'):
                            # Jika PNG transparan/warna banyak, kompres dengan quantize (palette) agar ukuran turun drastis
                            if img_resized.mode == "RGBA":
                                img_resized = img_resized.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
                            img_resized.save(img_buf, format="PNG", optimize=True, compress_level=zip_level)
                            
                        compressed_img = img_buf.getvalue()
                        # Gunakan gambar yang baru jika ukurannya lebih kecil
                        if len(compressed_img) < len(content):
                            content = compressed_img
                    except Exception:
                        pass
                
                # PERBAIKAN: Buat ZipInfo baru agar parameter 'compresslevel' benar-benar aktif
                zinfo = zipfile.ZipInfo(item.filename)
                zinfo.date_time = item.date_time
                zinfo.compress_type = zipfile.ZIP_DEFLATED
                out_zip.writestr(zinfo, content, compresslevel=zip_level)
                
    return out_buf.getvalue(), media_count


# ================= FUNGSI KOMPRESI PDF (DIPERBAIKI) =================
def compress_pdf_file(file_bytes, quality_slider=70):
    in_buf = io.BytesIO(file_bytes)
    reader = PdfReader(in_buf)
    writer = PdfWriter()
    
    deflate_level = max(1, min(9, int((100 - quality_slider) / 11) + 1))
    scale_factor = max(0.3, min(1.0, quality_slider / 100.0))
    
    for page in reader.pages:
        writer.add_page(page)
        
    for page in writer.pages:
        # 1. Kompres teks & streams dokumen
        try:
            page.compress_content_streams(level=deflate_level)
        except Exception:
            try:
                page.compress_content_streams()
            except Exception:
                pass
            
        # 2. Kompres & kecilkan resolusi gambar internal di PDF
        try:
            for img in page.images:
                try:
                    pil_img = img.image
                    
                    # Normalisasi mode gambar agar tidak gagal saat disimpan ulang
                    if pil_img.mode in ("RGBA", "LA", "P"):
                        bg = Image.new("RGB", pil_img.size, (255, 255, 255))
                        if pil_img.mode in ("RGBA", "LA"):
                            bg.paste(pil_img, mask=pil_img.split()[-1])
                        else:
                            bg.paste(pil_img.convert("RGB"))
                        pil_img = bg
                    elif pil_img.mode != "RGB":
                        pil_img = pil_img.convert("RGB")
                    
                    # Kecilkan resolusi gambar agar ukuran file turun drastis
                    if scale_factor < 1.0:
                        new_w = max(1, int(pil_img.width * scale_factor))
                        new_h = max(1, int(pil_img.height * scale_factor))
                        pil_img = pil_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
                    
                    # Ganti gambar lama dengan versi terkompresi
                    img.replace(pil_img, quality=quality_slider)
                except Exception:
                    pass
        except Exception:
            pass
            
    try:
        writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
    except Exception:
        pass
        
    out_buf = io.BytesIO()
    writer.write(out_buf)
    return out_buf.getvalue(), len(reader.pages)


# ================= 1. HALAMAN KOMPRES GAMBAR =================
if st.session_state.active_menu == "🖼️ Kompres Gambar":
    file_img = st.file_uploader("Upload Foto / Gambar (JPG, PNG)", type=["jpg", "jpeg", "png", "webp"])
    
    if file_img:
        img_original = Image.open(file_img)
        raw_bytes_awal = file_img.getvalue()
        bytes_awal = len(raw_bytes_awal)
        
        col1, col2 = st.columns(2)
        with col1:
            quality = st.slider("Kualitas Kompresi (%)", 10, 95, 70)
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
        bytes_akhir = len(res_img_bytes)
        
        hemat = ((bytes_awal - bytes_akhir) / bytes_awal) * 100 if bytes_awal > 0 else 0
        
        st.markdown(f"""
        <div class="metrics-container">
            <div class="metric-card">
                <div class="metric-label">Ukuran Asli</div>
                <div class="metric-value">{format_size(bytes_awal)}</div>
            </div>
            <div class="metric-card highlight">
                <div class="metric-label">Hasil Baru</div>
                <div class="metric-value">{format_size(bytes_akhir)}</div>
                <span class="badge-hemat">Hemat {hemat:.1f}%</span>
            </div>
            <div class="metric-card">
                <div class="metric-label">Resolusi</div>
                <div class="metric-value">{new_w}×{new_h}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.download_button(
            label=f"⬇️ Download Gambar ({format_size(bytes_akhir)})",
            data=res_img_bytes,
            file_name=f"compressed_{file_img.name.rsplit('.', 1)[0]}.jpg",
            mime="image/jpeg",
            use_container_width=True
        )

        st.markdown("""
        <div class="info-tip">
            🔍 <b>Pratinjau:</b> Geser tab di bawah untuk membandingkan kualitas gambar sebelum diunduh:
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
        bytes_awal_pdf = len(file_pdf.getvalue())
        
        # Slider interaktif PDF (Nilai berubah saat digeser)
        pdf_q = st.slider(
            "Tingkat Kualitas & Kompresi PDF (%)", 
            min_value=10, 
            max_value=95, 
            value=65,
            help="Geser ke kiri untuk memperkecil ukuran file secara maksimal."
        )
        
        try:
            res_pdf_bytes, total_pages = compress_pdf_file(file_pdf.getvalue(), quality_slider=pdf_q)
            bytes_akhir_pdf = len(res_pdf_bytes)
            
            hemat_pdf = ((bytes_awal_pdf - bytes_akhir_pdf) / bytes_awal_pdf) * 100 if bytes_awal_pdf > 0 else 0
            if hemat_pdf < 0:
                hemat_pdf = 0
            
            st.markdown(f"""
            <div class="metrics-container">
                <div class="metric-card">
                    <div class="metric-label">Ukuran Asli</div>
                    <div class="metric-value">{format_size(bytes_awal_pdf)}</div>
                </div>
                <div class="metric-card highlight">
                    <div class="metric-label">Hasil Baru</div>
                    <div class="metric-value">{format_size(bytes_akhir_pdf)}</div>
                    <span class="badge-hemat">Hemat {hemat_pdf:.1f}%</span>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Halaman</div>
                    <div class="metric-value">{total_pages} Hal</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.download_button(
                label=f"⬇️ Download PDF ({format_size(bytes_akhir_pdf)})",
                data=res_pdf_bytes,
                file_name=f"compressed_{file_pdf.name}",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Gagal memproses file PDF: {e}")


# ================= 3. HALAMAN KOMPRES OFFICE (WORD, PPT, EXCEL) =================
elif st.session_state.active_menu == "📊 Kompres Dokumen Office":
    file_office = st.file_uploader("Upload Dokumen Office (.docx, .pptx, .xlsx)", type=["docx", "pptx", "xlsx"])
    
    if file_office:
        bytes_awal_off = len(file_office.getvalue())
        ext_doc = file_office.name.rsplit('.', 1)[-1].upper()
        
        # Slider yang sekarang aktif memengaruhi tingkat kompresi data ZIP & media
        comp_level = st.slider(
            "Tingkat Kualitas & Kompresi Dokumen (%)", 
            min_value=10, 
            max_value=95, 
            value=60, 
            help="100% = Kompresi ringan (ukuran lebih besar). 10% = Kompresi maksimal (ukuran paling kecil)."
        )
        
        # Proses real-time di memori
        res_off_bytes, jumlah_media = compress_office_file(file_office.getvalue(), quality_slider=comp_level)
        bytes_akhir_off = len(res_off_bytes)
        
        hemat_off = ((bytes_awal_off - bytes_akhir_off) / bytes_awal_off) * 100 if bytes_awal_off > 0 else 0
        if hemat_off < 0:
            hemat_off = 0
            
        label_info_ketiga = f"{jumlah_media} Gambar" if jumlah_media > 0 else f"{ext_doc}"

        st.markdown(f"""
        <div class="metrics-container">
            <div class="metric-card">
                <div class="metric-label">Ukuran Asli</div>
                <div class="metric-value">{format_size(bytes_awal_off)}</div>
            </div>
            <div class="metric-card highlight">
                <div class="metric-label">Hasil Baru</div>
                <div class="metric-value">{format_size(bytes_akhir_off)}</div>
                <span class="badge-hemat">Hemat {hemat_off:.1f}%</span>
            </div>
            <div class="metric-card">
                <div class="metric-label">Tipe Media</div>
                <div class="metric-value">{label_info_ketiga}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if jumlah_media == 0:
            st.markdown("""
            <div class="info-tip">
                ℹ️ <b>Info Dokumen Teks:</b> File ini tidak memuat foto/gambar. Perubahan angka di atas murni berasal dari tingkat pemadatan struktur tabel/teks dokumen (Level 1–9).
            </div>
            """, unsafe_allow_html=True)
        
        st.download_button(
            label=f"⬇️ Download Dokumen {ext_doc} ({format_size(bytes_akhir_off)})",
            data=res_off_bytes,
            file_name=f"optimized_{file_office.name}",
            mime="application/octet-stream",
            use_container_width=True
        )
