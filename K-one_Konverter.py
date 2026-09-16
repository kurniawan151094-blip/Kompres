import streamlit as st
import io
import time
import zipfile
import streamlit.components.v1 as components
from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject

# ================= KONFIGURASI HALAMAN =================
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

    /* TOMBOL HAMBURGER */
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

    /* TOMBOL SIDEBAR */
    [data-testid="stSidebar"] .stButton > button {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        padding: 0.95rem 1.2rem !important;
        margin-bottom: 0.7rem !important;
        border-radius: 12px !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }

    /* HEADER */
    .brand-header {
        text-align: center;
        margin-top: 0.2rem;
        margin-bottom: 1.2rem;
    }
    .brand-title {
        font-size: 1.85rem;
        font-weight: 800;
        background: linear-gradient(90deg, #2563EB, #7C3AED);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .brand-sub {
        font-size: 0.92rem;
        color: #64748B;
        font-weight: 600;
        margin-top: 4px;
    }

    /* KARTU METRIK STATISTIK */
    .metrics-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin: 1.2rem 0;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 12px 6px;
        text-align: center;
        transition: all 0.2s ease;
    }
    .metric-card.highlight {
        background: #EFF6FF;
        border: 1.5px solid #93C5FD;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08);
    }
    .metric-label {
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #64748B;
        letter-spacing: 0.4px;
    }
    .metric-value {
        font-size: 1.05rem;
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
        padding: 2px 8px;
        border-radius: 999px;
        margin-top: 4px;
    }

    /* KOTAK TIP */
    .info-tip {
        background: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 10px 14px;
        border-radius: 8px;
        font-size: 0.83rem;
        color: #475569;
        margin: 1rem 0;
    }

    /* TOMBOL DOWNLOAD PRO */
    [data-testid="stDownloadButton"] {
        margin-top: 10px;
        margin-bottom: 12px;
    }
    [data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 50%, #7C3AED 100%) !important;
        color: #FFFFFF !important;
        font-size: 1.05rem !important;
        font-weight: 800 !important;
        padding: 0.95rem 1.6rem !important;
        border-radius: 14px !important;
        border: none !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45) !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        letter-spacing: 0.3px;
    }
    [data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 28px rgba(124, 58, 237, 0.55) !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)


# ================= HELPER FUNCTIONS =================
def format_size(size_in_bytes):
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    kb = size_in_bytes / 1024
    if kb >= 1024:
        return f"{kb / 1024:.2f} MB"
    return f"{kb:.2f} KB"

def show_download_loading_bar(file_type="berkas"):
    loading_box = st.empty()
    prog_bar = loading_box.progress(0, text=f"⚡ Menyiapkan unduhan {file_type}...")
    for pct, msg in [(30, "📦 Memadatkan berkas..."), (75, "⚡ Mengemas hasil kompresi..."), (100, "✅ Berkas siap!")]:
        time.sleep(0.06)
        prog_bar.progress(pct, text=msg)
    time.sleep(0.15)
    loading_box.empty()
    st.toast(f"🎉 Berkas {file_type} berhasil diunduh!", icon="📥")


# ================= STATE NAVIGASI =================
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "🖼️ Kompres Gambar"

if "close_sidebar_trigger" not in st.session_state:
    st.session_state.close_sidebar_trigger = False

if st.session_state.close_sidebar_trigger:
    st.session_state.close_sidebar_trigger = False
    components.html(f"""
        <script>
            setTimeout(function() {{
                try {{
                    const parentDoc = window.parent.document;
                    const closeBtn = parentDoc.querySelector('[data-testid="stSidebarCollapseButton"] button') ||
                                     parentDoc.querySelector('button[aria-label="Close sidebar"]');
                    if (closeBtn) closeBtn.click();
                }} catch (e) {{}}
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


# ================= REALTIME ENGINE: OFFICE =================
def compress_office_file(file_bytes, quality_slider=70):
    bytes_asli = len(file_bytes)
    in_buf = io.BytesIO(file_bytes)
    out_buf = io.BytesIO()
    media_count = 0
    
    # Skala resolusi langsung terikat linier dengan slider (seperti kompresi gambar)
    scale_factor = max(0.15, min(1.0, quality_slider / 100.0))
    target_q = max(15, min(90, quality_slider))
    zip_level = 9 if quality_slider <= 75 else 6
    
    with zipfile.ZipFile(in_buf, 'r') as in_zip:
        with zipfile.ZipFile(out_buf, 'w') as out_zip:
            for item in in_zip.infolist():
                content = in_zip.read(item.filename)
                fname_lower = item.filename.lower()
                
                is_img = any(fname_lower.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.webp'))
                is_media = any(f in fname_lower for f in ('media/', 'pictures/'))
                
                if is_img and is_media:
                    media_count += 1
                    try:
                        img = Image.open(io.BytesIO(content))
                        img_buf = io.BytesIO()
                        
                        # Downscale dimensi piksel secara nyata
                        new_w = max(1, int(img.width * scale_factor))
                        new_h = max(1, int(img.height * scale_factor))
                        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                        
                        if fname_lower.endswith(('.jpg', '.jpeg')):
                            if img_resized.mode in ("RGBA", "P"):
                                img_resized = img_resized.convert("RGB")
                            img_resized.save(img_buf, format="JPEG", quality=target_q, optimize=True)
                            content = img_buf.getvalue()
                            
                        elif fname_lower.endswith('.png'):
                            # Palette Quantization dinamis sesuai slider
                            num_colors = max(16, min(256, int(256 * scale_factor)))
                            if img_resized.mode != "RGBA":
                                img_p = img_resized.convert("RGB").convert("P", palette=Image.Palette.ADAPTIVE, colors=num_colors)
                            else:
                                img_p = img_resized.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)
                            
                            img_p.save(img_buf, format="PNG", optimize=True, compress_level=9)
                            content = img_buf.getvalue()
                    except Exception:
                        pass
                
                zinfo = zipfile.ZipInfo(item.filename)
                zinfo.date_time = item.date_time
                zinfo.compress_type = zipfile.ZIP_DEFLATED
                out_zip.writestr(zinfo, content, compresslevel=zip_level)
                
    hasil_bytes = out_buf.getvalue()
    
    # Jamin hasil tidak melebihi file asli
    if len(hasil_bytes) > bytes_asli:
        hasil_bytes = file_bytes
        
    return hasil_bytes, media_count


# ================= REALTIME ENGINE: PDF =================
def compress_pdf_file(file_bytes, quality_slider=70):
    bytes_asli = len(file_bytes)
    in_buf = io.BytesIO(file_bytes)
    reader = PdfReader(in_buf)
    writer = PdfWriter()
    
    total_pages = len(reader.pages)
    for page in reader.pages:
        writer.add_page(page)
        
    try:
        writer.add_metadata({})
    except Exception:
        pass

    # Skala resolusi langsung terikat linier dengan slider (seperti gambar)
    scale_factor = max(0.2, min(0.95, quality_slider / 100.0))
    target_q = max(15, min(85, quality_slider))
    deflate_lvl = 9 if quality_slider <= 70 else 6
    
    image_count = 0
    for page in writer.pages:
        # Kompres konten teks & stream dokumen
        try:
            page.compress_content_streams(level=deflate_lvl)
        except Exception:
            pass
            
        # Pindai dan kompres semua gambar internal di setiap halaman PDF
        try:
            for img in page.images:
                image_count += 1
                try:
                    pil_img = img.image
                    
                    # 1. Kecilkan resolusi gambar mengikuti slider
                    new_w = max(1, int(pil_img.width * scale_factor))
                    new_h = max(1, int(pil_img.height * scale_factor))
                    if new_w < pil_img.width or new_h < pil_img.height:
                        pil_img = pil_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
                        
                    # 2. Normalisasi format gambar
                    if pil_img.mode in ("RGBA", "LA", "P"):
                        bg = Image.new("RGB", pil_img.size, (255, 255, 255))
                        if pil_img.mode in ("RGBA", "LA"):
                            bg.paste(pil_img, mask=pil_img.split()[-1])
                        else:
                            bg.paste(pil_img.convert("RGB"))
                        pil_img = bg
                    elif pil_img.mode != "RGB":
                        pil_img = pil_img.convert("RGB")
                    
                    # 3. Ganti gambar dengan versi terkompresi baru
                    img.replace(pil_img, quality=target_q)
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
    hasil_bytes = out_buf.getvalue()
    
    # Jamin hasil tidak melebihi file asli
    if len(hasil_bytes) > bytes_asli:
        hasil_bytes = file_bytes
        
    return hasil_bytes, total_pages, image_count


# ================= 1. MENU KOMPRES GAMBAR =================
if st.session_state.active_menu == "🖼️ Kompres Gambar":
    file_img = st.file_uploader("Upload Foto / Gambar (JPG, PNG, WebP)", type=["jpg", "jpeg", "png", "webp"])
    
    if file_img:
        raw_bytes_awal = file_img.getvalue()
        bytes_awal = len(raw_bytes_awal)
        img_original = Image.open(io.BytesIO(raw_bytes_awal))
        
        col1, col2 = st.columns(2)
        with col1:
            quality = st.slider("Kualitas Kompresi (%)", 10, 95, 70)
        with col2:
            scale = st.slider("Skala Resolusi (%)", 10, 100, 100)

        # Logika pemrosesan real-time
        new_w = max(1, int(img_original.width * (scale / 100)))
        new_h = max(1, int(img_original.height * (scale / 100)))
        img_proses = img_original.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        if img_proses.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img_proses.size, (255, 255, 255))
            if img_proses.mode in ("RGBA", "LA"):
                bg.paste(img_proses, mask=img_proses.split()[-1])
            else:
                bg.paste(img_proses.convert("RGB"))
            img_proses = bg
        elif img_proses.mode != "RGB":
            img_proses = img_proses.convert("RGB")
            
        out_img = io.BytesIO()
        img_proses.save(out_img, format="JPEG", quality=quality, optimize=True)
        res_img_bytes = out_img.getvalue()
        
        if len(res_img_bytes) > bytes_awal and scale == 100:
            res_img_bytes = raw_bytes_awal
            
        bytes_akhir = len(res_img_bytes)
        hemat = ((bytes_awal - bytes_akhir) / bytes_awal) * 100 if bytes_awal > bytes_akhir else 0.0
        
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

        btn_download_img = st.download_button(
            label=f"⬇️ DOWNLOAD GAMBAR ({format_size(bytes_akhir)})",
            data=res_img_bytes,
            file_name=f"compressed_{file_img.name.rsplit('.', 1)[0]}.jpg",
            mime="image/jpeg",
            use_container_width=True,
            key="btn_download_image"
        )
        if btn_download_img:
            show_download_loading_bar("Gambar")

        tab_hasil, tab_asli = st.tabs(["✨ Hasil Baru", "🔍 Foto Asli"])
        with tab_hasil:
            st.image(res_img_bytes, caption=f"Hasil Baru ({new_w} × {new_h} px)", use_container_width=True)
        with tab_asli:
            st.image(file_img, caption=f"Foto Asli ({img_original.width} × {img_original.height} px)", use_container_width=True)


# ================= 2. MENU KOMPRES PDF =================
elif st.session_state.active_menu == "📄 Kompres Dokumen PDF":
    file_pdf = st.file_uploader("Upload Dokumen PDF", type=["pdf"])
    
    if file_pdf:
        bytes_awal_pdf = len(file_pdf.getvalue())
        
        pdf_q = st.slider(
            "Tingkat Kualitas & Kompresi PDF (%)", 
            min_value=10, 
            max_value=90, 
            value=60,
            help="Geser ke kiri untuk memperkecil ukuran file secara maksimal."
        )
        
        try:
            # Memproses kompresi secara real-time seperti gambar
            res_pdf_bytes, total_pages, total_img = compress_pdf_file(file_pdf.getvalue(), quality_slider=pdf_q)
            bytes_akhir_pdf = len(res_pdf_bytes)
            
            if bytes_awal_pdf > bytes_akhir_pdf:
                hemat_pdf = ((bytes_awal_pdf - bytes_akhir_pdf) / bytes_awal_pdf) * 100
            else:
                hemat_pdf = 0.0
                bytes_akhir_pdf = bytes_awal_pdf
            
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
                    <div class="metric-label">Halaman / Gambar</div>
                    <div class="metric-value">{total_pages} Hal / {total_img} Gbr</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if total_img == 0:
                st.markdown("""
                <div class="info-tip">
                    ℹ️ <b>PDF Berbasis Vektor:</b> Dokumen ini tidak memuat elemen foto/gambar (murni teks & font sistem). Penurunan ukuran berasal dari pemadatan teks stream & pembersihan objek sampah.
                </div>
                """, unsafe_allow_html=True)
            
            btn_download_pdf = st.download_button(
                label=f"⬇️ DOWNLOAD PDF ({format_size(bytes_akhir_pdf)})",
                data=res_pdf_bytes,
                file_name=f"compressed_{file_pdf.name}",
                mime="application/pdf",
                use_container_width=True,
                key="btn_download_pdf_file"
            )
            if btn_download_pdf:
                show_download_loading_bar("PDF")
                
        except Exception as e:
            st.error(f"Gagal memproses file PDF: {e}")


# ================= 3. MENU KOMPRES OFFICE =================
elif st.session_state.active_menu == "📊 Kompres Dokumen Office":
    file_office = st.file_uploader("Upload Dokumen Office (.docx, .pptx, .xlsx)", type=["docx", "pptx", "xlsx"])
    
    if file_office:
        bytes_awal_off = len(file_office.getvalue())
        ext_doc = file_office.name.rsplit('.', 1)[-1].upper()
        
        comp_level = st.slider(
            "Tingkat Kualitas & Kompresi Dokumen (%)", 
            min_value=10, 
            max_value=90, 
            value=60, 
            help="Geser ke kiri untuk memperkecil ukuran media & dokumen secara maksimal."
        )
        
        # Memproses kompresi secara real-time seperti gambar
        res_off_bytes, jumlah_media = compress_office_file(file_office.getvalue(), quality_slider=comp_level)
        bytes_akhir_off = len(res_off_bytes)
        
        if bytes_awal_off > bytes_akhir_off:
            hemat_off = ((bytes_awal_off - bytes_akhir_off) / bytes_awal_off) * 100
        else:
            hemat_off = 0.0
            bytes_akhir_off = bytes_awal_off
            
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
                <div class="metric-label">Aset Media</div>
                <div class="metric-value">{label_info_ketiga}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if jumlah_media == 0:
            st.markdown("""
            <div class="info-tip">
                ℹ️ <b>Dokumen Teks Murni:</b> Berkas ini tidak memuat foto/gambar. Penghematan ukuran dioptimalkan melalui pemadatan struktur XML dokumen secara maksimal (Level 9).
            </div>
            """, unsafe_allow_html=True)
        
        btn_download_office = st.download_button(
            label=f"⬇️ DOWNLOAD DOKUMEN {ext_doc} ({format_size(bytes_akhir_off)})",
            data=res_off_bytes,
            file_name=f"optimized_{file_office.name}",
            mime="application/octet-stream",
            use_container_width=True,
            key="btn_download_office_file"
        )
        if btn_download_office:
            show_download_loading_bar(f"Dokumen {ext_doc}")
