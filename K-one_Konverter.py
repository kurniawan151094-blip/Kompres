import streamlit as st
import io
import time
import zipfile
import streamlit.components.v1 as components
from PIL import Image
from pypdf import PdfReader, PdfWriter

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(
    page_title="CompressPro - Batch Compressor",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= CUSTOM CSS (RESPONSIF, FLOATING LOADER READY) =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* 1. HEADER TRANSPARAN */
    header[data-testid="stHeader"] {
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* Sembunyikan tombol bawaan Streamlit yang tidak diperlukan */
    [data-testid="stToolbarActions"],
    [data-testid="stStatusWidget"],
    .stDeployButton,
    #MainMenu,
    [data-testid="stHeaderActionElements"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* 2. TOMBOL HAMBURGER ASLI (>>) BESAR & SELALU AKTIF */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: fixed !important;
        top: 14px !important;
        left: 14px !important;
        z-index: 9999999 !important;
    }

    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="collapsedControl"] button {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: 50px !important;
        height: 50px !important;
        background: linear-gradient(135deg, #2563EB, #4F46E5) !important;
        border-radius: 14px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.45) !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }

    [data-testid="stSidebarCollapsedControl"] button:hover,
    [data-testid="collapsedControl"] button:hover {
        transform: scale(1.06) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.6) !important;
    }

    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="collapsedControl"] svg {
        display: block !important;
        visibility: visible !important;
        width: 28px !important;
        height: 28px !important;
        stroke: #ffffff !important;
        fill: #ffffff !important;
        color: #ffffff !important;
    }

    /* 3. LAYOUT KONTEN */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 680px;
    }

    [data-testid="stSidebar"] .stButton > button {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        padding: 0.95rem 1.2rem !important;
        margin-bottom: 0.7rem !important;
        border-radius: 12px !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }

    /* 4. DESAIN JUDUL BERSENI */
    .brand-hero {
        position: relative;
        text-align: center;
        padding: 0.2rem 0 0.8rem 0;
        margin-top: 0.2rem;
        margin-bottom: 0.8rem;
    }

    .brand-hero::before {
        content: "";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 260px;
        height: 80px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.28) 0%, rgba(236, 72, 153, 0.15) 50%, transparent 75%);
        filter: blur(24px);
        z-index: 0;
        pointer-events: none;
    }

    .brand-pill {
        position: relative;
        z-index: 1;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 3px 12px;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        border-radius: 999px;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.28);
        color: #6366F1;
        margin-bottom: 6px;
        backdrop-filter: blur(6px);
    }

    .brand-title {
        position: relative;
        z-index: 1;
        font-size: 2.35rem;
        font-weight: 900;
        letter-spacing: -0.8px;
        line-height: 1.1;
        margin: 0;
        display: inline-block;
        background: linear-gradient(125deg, #0284C7 0%, #6366F1 45%, #EC4899 90%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 4px 14px rgba(99, 102, 241, 0.35));
    }

    .brand-title .pro-badge {
        font-size: 0.95rem;
        vertical-align: super;
        margin-left: 4px;
        padding: 2px 7px;
        border-radius: 7px;
        font-weight: 900;
        letter-spacing: 0.5px;
        background: linear-gradient(135deg, #EC4899, #8B5CF6);
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(236, 72, 153, 0.4);
    }

    .brand-divider {
        position: relative;
        z-index: 1;
        width: 48px;
        height: 4px;
        background: linear-gradient(90deg, #0284C7, #6366F1, #EC4899);
        border-radius: 99px;
        margin: 6px auto 9px auto;
    }

    .brand-sub {
        position: relative;
        z-index: 1;
        display: inline-flex;
        align-items: center;
        gap: 7px;
        font-size: 0.86rem;
        color: #64748B;
        font-weight: 600;
        background: rgba(148, 163, 184, 0.1);
        padding: 4px 14px;
        border-radius: 20px;
        border: 1px solid rgba(148, 163, 184, 0.2);
    }

    .pulse-dot {
        width: 7px;
        height: 7px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10B981;
        animation: pulse 1.8s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.9); opacity: 0.7; }
        50% { transform: scale(1.3); opacity: 1; box-shadow: 0 0 12px #10B981; }
        100% { transform: scale(0.9); opacity: 0.7; }
    }

    /* 5. KARTU METRIK TOTAL */
    .metrics-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin: 1.1rem 0;
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

    /* 6. TOMBOL DOWNLOAD BESAR (ZIP) */
    [data-testid="stDownloadButton"] {
        margin-top: 8px;
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

    /* 7. TOMBOL UNDUH SATUAN DI DALAM EXPANDER */
    div[data-testid="stExpander"] [data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #2563EB, #4F46E5) !important;
        color: #FFFFFF !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        padding: 0.45rem 0.9rem !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3) !important;
        margin: 0 !important;
    }
    div[data-testid="stExpander"] [data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.45) !important;
    }
</style>
""", unsafe_allow_html=True)


# ================= WADAH UTAMA FLOATING HUD (GLOBAL ROOT SLOT) =================
# Diletakkan di root agar tidak pernah terpotong/terjebak di dalam kolom atau expander
hud_slot = st.empty()


# ================= HELPER UKURAN FILE =================
def format_size(size_in_bytes):
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    kb = size_in_bytes / 1024
    if kb >= 1024:
        return f"{kb / 1024:.2f} MB"
    return f"{kb:.2f} KB"


# ================= VISUAL LOADING MELAYANG (FLOATING HUD) =================
def show_download_loading(kategori="gambar", is_bundle=False, file_name=None):
    """Menampilkan progress bar melayang di atas layar dari level root selama ~2.5 detik"""
    nama_label = "Bundle ZIP" if is_bundle else (f"'{file_name}'" if file_name else "Berkas")
    
    stages = [
        (18, f"⚡ Menginisialisasi transfer {nama_label}...", 0.4),
        (42, "📦 Memadatkan & mengemas data berkas...", 0.5),
        (72, "⚡ Mengoptimalkan paket kompresi...", 0.6),
        (92, "🚀 Menyinkronkan unduhan ke perangkat...", 0.5),
        (100, "✅ Selesai! Berkas siap diunduh...", 0.45)
    ]
    
    for pct, msg, delay in stages:
        floating_html = f"""
        <div style="
            position: fixed;
            top: 22px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 99999999;
            width: min(90vw, 440px);
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            border: 1.5px solid rgba(99, 102, 241, 0.55);
            border-radius: 18px;
            padding: 14px 20px;
            box-shadow: 0 14px 40px rgba(0, 0, 0, 0.5), 0 0 25px rgba(99, 102, 241, 0.35);
            font-family: 'Plus Jakarta Sans', sans-serif;
            pointer-events: none;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 9px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="display: inline-block; width: 10px; height: 10px; background: #10B981; border-radius: 50%; box-shadow: 0 0 10px #10B981;"></span>
                    <span style="color: #F8FAFC; font-weight: 800; font-size: 0.88rem; letter-spacing: 0.5px;">MEMPROSES UNDUHAN</span>
                </div>
                <span style="color: #EC4899; font-weight: 800; font-size: 0.9rem;">{pct}%</span>
            </div>
            
            <div style="width: 100%; height: 8px; background: rgba(255, 255, 255, 0.12); border-radius: 99px; overflow: hidden; margin-bottom: 9px;">
                <div style="width: {pct}%; height: 100%; background: linear-gradient(90deg, #0284C7 0%, #6366F1 50%, #EC4899 100%); border-radius: 99px; transition: width 0.35s ease;"></div>
            </div>
            
            <div style="color: #94A3B8; font-size: 0.78rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                {msg}
            </div>
        </div>
        """
        hud_slot.markdown(floating_html, unsafe_allow_html=True)
        time.sleep(delay)
        
    hud_slot.empty()
    
    # Notifikasi spesifik sesuai permintaan
    if kategori == "gambar":
        teks_notif = "Gambar berhasil diunduh"
    elif kategori in ("pdf", "office"):
        teks_notif = "Dokumen berhasil diunduh"
    else:
        teks_notif = "File berhasil diunduh"
        
    st.toast(f"🎉 {teks_notif}!", icon="✅")


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
<div class="brand-hero">
    <div class="brand-pill">⚡ NEXT-GEN COMPRESSION</div><br>
    <div class="brand-title">Compress<span class="pro-badge">PRO</span></div>
    <div class="brand-divider"></div>
    <div class="brand-sub">
        <span class="pulse-dot"></span>
        <span>{st.session_state.active_menu} • Multi-File Ready</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ================= ENGINE KOMPRESI GAMBAR INDIVIDUAL =================
def compress_single_image(raw_bytes, quality=70, scale=100):
    bytes_asli = len(raw_bytes)
    try:
        img_original = Image.open(io.BytesIO(raw_bytes))
        new_w = max(1, int(img_original.width * (scale / 100.0)))
        new_h = max(1, int(img_original.height * (scale / 100.0)))
        
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
        res_bytes = out_img.getvalue()
        
        if len(res_bytes) > bytes_asli and scale == 100:
            res_bytes = raw_bytes
            
        return res_bytes, f"{new_w}×{new_h}"
    except Exception:
        return raw_bytes, "Error"


# ================= ENGINE KOMPRESI PDF INDIVIDUAL =================
def compress_single_pdf(raw_bytes, quality_slider=70):
    bytes_asli = len(raw_bytes)
    try:
        in_buf = io.BytesIO(raw_bytes)
        reader = PdfReader(in_buf)
        writer = PdfWriter()
        
        total_pages = len(reader.pages)
        for page in reader.pages:
            writer.add_page(page)
            
        try:
            writer.add_metadata({})
        except Exception:
            pass

        scale_factor = max(0.2, min(0.95, quality_slider / 100.0))
        target_q = max(15, min(85, quality_slider))
        deflate_lvl = 9 if quality_slider <= 70 else 6
        
        for page in writer.pages:
            try:
                page.compress_content_streams(level=deflate_lvl)
            except Exception:
                pass
                
            try:
                for img in page.images:
                    try:
                        pil_img = img.image
                        new_w = max(1, int(pil_img.width * scale_factor))
                        new_h = max(1, int(pil_img.height * scale_factor))
                        if new_w < pil_img.width or new_h < pil_img.height:
                            pil_img = pil_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
                            
                        if pil_img.mode in ("RGBA", "LA", "P"):
                            bg = Image.new("RGB", pil_img.size, (255, 255, 255))
                            if pil_img.mode in ("RGBA", "LA"):
                                bg.paste(pil_img, mask=pil_img.split()[-1])
                            else:
                                bg.paste(pil_img.convert("RGB"))
                            pil_img = bg
                        elif pil_img.mode != "RGB":
                            pil_img = pil_img.convert("RGB")
                            
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
        
        if len(hasil_bytes) > bytes_asli:
            hasil_bytes = raw_bytes
            
        return hasil_bytes, total_pages
    except Exception:
        return raw_bytes, 0


# ================= ENGINE KOMPRESI OFFICE INDIVIDUAL =================
def compress_single_office(raw_bytes, quality_slider=70):
    bytes_asli = len(raw_bytes)
    try:
        in_buf = io.BytesIO(raw_bytes)
        out_buf = io.BytesIO()
        
        scale_factor = max(0.15, min(1.0, quality_slider / 100.0))
        target_q = max(15, min(90, quality_slider))
        zip_lvl = 9 if quality_slider <= 75 else 6
        
        with zipfile.ZipFile(in_buf, 'r') as in_zip:
            with zipfile.ZipFile(out_buf, 'w') as out_zip:
                for item in in_zip.infolist():
                    content = in_zip.read(item.filename)
                    fname_lower = item.filename.lower()
                    
                    is_img = any(fname_lower.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.webp'))
                    is_media = any(f in fname_lower for f in ('media/', 'pictures/'))
                    
                    if is_img and is_media:
                        try:
                            img = Image.open(io.BytesIO(content))
                            img_buf = io.BytesIO()
                            
                            new_w = max(1, int(img.width * scale_factor))
                            new_h = max(1, int(img.height * scale_factor))
                            img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                            
                            if fname_lower.endswith(('.jpg', '.jpeg')):
                                if img_resized.mode in ("RGBA", "P"):
                                    img_resized = img_resized.convert("RGB")
                                img_resized.save(img_buf, format="JPEG", quality=target_q, optimize=True)
                                content = img_buf.getvalue()
                                
                            elif fname_lower.endswith('.png'):
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
                    out_zip.writestr(zinfo, content, compresslevel=zip_lvl)
                    
        hasil_bytes = out_buf.getvalue()
        if len(hasil_bytes) > bytes_asli:
            hasil_bytes = raw_bytes
            
        return hasil_bytes
    except Exception:
        return raw_bytes


# ================= 1. MENU KOMPRES GAMBAR (BATCH) =================
if st.session_state.active_menu == "🖼️ Kompres Gambar":
    files_img = st.file_uploader(
        "Upload Foto / Gambar (Bisa pilih banyak sekaligus)", 
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True
    )
    
    if files_img:
        col1, col2 = st.columns(2)
        with col1:
            quality = st.slider("Kualitas Kompresi (%)", 10, 95, 70)
        with col2:
            scale = st.slider("Skala Resolusi (%)", 10, 100, 100)

        total_awal = 0
        total_akhir = 0
        list_hasil = []
        
        for file in files_img:
            raw_bytes = file.getvalue()
            b_awal = len(raw_bytes)
            total_awal += b_awal
            
            res_bytes, info_res = compress_single_image(raw_bytes, quality=quality, scale=scale)
            b_akhir = len(res_bytes)
            total_akhir += b_akhir
            
            out_filename = f"compressed_{file.name.rsplit('.', 1)[0]}.jpg"
            list_hasil.append({
                "name": file.name,
                "out_name": out_filename,
                "awal": b_awal,
                "akhir": b_akhir,
                "bytes": res_bytes,
                "mime": "image/jpeg",
                "extra": info_res
            })

        total_hemat = ((total_awal - total_akhir) / total_awal) * 100 if total_awal > total_akhir else 0.0

        st.markdown(f"""
        <div class="metrics-container">
            <div class="metric-card">
                <div class="metric-label">Total Ukuran Asli</div>
                <div class="metric-value">{format_size(total_awal)}</div>
            </div>
            <div class="metric-card highlight">
                <div class="metric-label">Total Hasil Baru</div>
                <div class="metric-value">{format_size(total_akhir)}</div>
                <span class="badge-hemat">Hemat {total_hemat:.1f}%</span>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Berkas</div>
                <div class="metric-value">{len(files_img)} Foto</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as z:
            for item in list_hasil:
                z.writestr(item["out_name"], item["bytes"])
        zip_bytes = zip_buf.getvalue()

        # Tombol Download ZIP (Memanggil hud_slot global)
        btn_zip = st.download_button(
            label=f"⬇️ DOWNLOAD SEMUA ({len(files_img)} GAMBAR) - ZIP ({format_size(len(zip_bytes))})",
            data=zip_bytes,
            file_name="CompressPro_Images_Bundle.zip",
            mime="application/zip",
            use_container_width=True,
            key="btn_download_zip_img"
        )
        if btn_zip:
            show_download_loading(kategori="gambar", is_bundle=True)

        # Rincian Unduh Satuan (Juga Memanggil hud_slot global)
        with st.expander("📋 Rincian & Unduh Satuan Tiap Gambar", expanded=True):
            for i, item in enumerate(list_hasil):
                item_hemat = ((item["awal"] - item["akhir"]) / item["awal"]) * 100 if item["awal"] > item["akhir"] else 0.0
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"**{item['name']}**")
                    st.caption(f"{format_size(item['awal'])} ➔ **{format_size(item['akhir'])}** (Hemat {item_hemat:.1f}%) | {item['extra']}")
                with c2:
                    btn_single = st.download_button(
                        label="⬇️ Unduh",
                        data=item["bytes"],
                        file_name=item["out_name"],
                        mime=item["mime"],
                        key=f"dl_single_img_{i}",
                        use_container_width=True
                    )
                    if btn_single:
                        show_download_loading(kategori="gambar", is_bundle=False, file_name=item["name"])


# ================= 2. MENU KOMPRES PDF (BATCH) =================
elif st.session_state.active_menu == "📄 Kompres Dokumen PDF":
    files_pdf = st.file_uploader(
        "Upload Dokumen PDF (Bisa pilih banyak sekaligus)", 
        type=["pdf"],
        accept_multiple_files=True
    )
    
    if files_pdf:
        pdf_q = st.slider(
            "Tingkat Kualitas & Kompresi PDF (%)", 
            min_value=10, 
            max_value=90, 
            value=60,
            help="Semakin kecil persentase, kompresi gambar di dalam PDF akan semakin padat."
        )
        
        total_awal_pdf = 0
        total_akhir_pdf = 0
        list_hasil_pdf = []
        
        for file in files_pdf:
            raw_bytes = file.getvalue()
            b_awal = len(raw_bytes)
            total_awal_pdf += b_awal
            
            res_bytes, pages = compress_single_pdf(raw_bytes, quality_slider=pdf_q)
            b_akhir = len(res_bytes)
            total_akhir_pdf += b_akhir
            
            out_filename = f"compressed_{file.name}"
            list_hasil_pdf.append({
                "name": file.name,
                "out_name": out_filename,
                "awal": b_awal,
                "akhir": b_akhir,
                "bytes": res_bytes,
                "mime": "application/pdf",
                "extra": f"{pages} Hal"
            })

        total_hemat_pdf = ((total_awal_pdf - total_akhir_pdf) / total_awal_pdf) * 100 if total_awal_pdf > total_akhir_pdf else 0.0

        st.markdown(f"""
        <div class="metrics-container">
            <div class="metric-card">
                <div class="metric-label">Total Ukuran Asli</div>
                <div class="metric-value">{format_size(total_awal_pdf)}</div>
            </div>
            <div class="metric-card highlight">
                <div class="metric-label">Total Hasil Baru</div>
                <div class="metric-value">{format_size(total_akhir_pdf)}</div>
                <span class="badge-hemat">Hemat {total_hemat_pdf:.1f}%</span>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Dokumen</div>
                <div class="metric-value">{len(files_pdf)} PDF</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        zip_buf_pdf = io.BytesIO()
        with zipfile.ZipFile(zip_buf_pdf, 'w', zipfile.ZIP_DEFLATED) as z:
            for item in list_hasil_pdf:
                z.writestr(item["out_name"], item["bytes"])
        zip_bytes_pdf = zip_buf_pdf.getvalue()

        # Tombol Download ZIP (Memanggil hud_slot global)
        btn_zip_pdf = st.download_button(
            label=f"⬇️ DOWNLOAD SEMUA ({len(files_pdf)} PDF) - ZIP ({format_size(len(zip_bytes_pdf))})",
            data=zip_bytes_pdf,
            file_name="CompressPro_PDF_Bundle.zip",
            mime="application/zip",
            use_container_width=True,
            key="btn_download_zip_pdf"
        )
        if btn_zip_pdf:
            show_download_loading(kategori="pdf", is_bundle=True)

        # Rincian Unduh Satuan (Juga Memanggil hud_slot global)
        with st.expander("📋 Rincian & Unduh Satuan Tiap PDF", expanded=True):
            for i, item in enumerate(list_hasil_pdf):
                item_hemat = ((item["awal"] - item["akhir"]) / item["awal"]) * 100 if item["awal"] > item["akhir"] else 0.0
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"**{item['name']}**")
                    st.caption(f"{format_size(item['awal'])} ➔ **{format_size(item['akhir'])}** (Hemat {item_hemat:.1f}%) | {item['extra']}")
                with c2:
                    btn_single_pdf = st.download_button(
                        label="⬇️ Unduh",
                        data=item["bytes"],
                        file_name=item["out_name"],
                        mime=item["mime"],
                        key=f"dl_single_pdf_{i}",
                        use_container_width=True
                    )
                    if btn_single_pdf:
                        show_download_loading(kategori="pdf", is_bundle=False, file_name=item["name"])


# ================= 3. MENU KOMPRES OFFICE (BATCH) =================
elif st.session_state.active_menu == "📊 Kompres Dokumen Office":
    files_off = st.file_uploader(
        "Upload Dokumen Office (.docx, .pptx, .xlsx) (Bisa pilih banyak)", 
        type=["docx", "pptx", "xlsx"],
        accept_multiple_files=True
    )
    
    if files_off:
        comp_level = st.slider(
            "Tingkat Kualitas & Kompresi Dokumen (%)", 
            min_value=10, 
            max_value=90, 
            value=60, 
            help="Geser ke kiri untuk memperkecil ukuran media dan struktur XML dokumen secara maksimal."
        )
        
        total_awal_off = 0
        total_akhir_off = 0
        list_hasil_off = []
        
        for file in files_off:
            raw_bytes = file.getvalue()
            b_awal = len(raw_bytes)
            total_awal_off += b_awal
            
            res_bytes = compress_single_office(raw_bytes, quality_slider=comp_level)
            b_akhir = len(res_bytes)
            total_akhir_off += b_akhir
            
            out_filename = f"optimized_{file.name}"
            list_hasil_off.append({
                "name": file.name,
                "out_name": out_filename,
                "awal": b_awal,
                "akhir": b_akhir,
                "bytes": res_bytes,
                "mime": "application/octet-stream"
            })

        total_hemat_off = ((total_awal_off - total_akhir_off) / total_awal_off) * 100 if total_awal_off > total_akhir_off else 0.0

        st.markdown(f"""
        <div class="metrics-container">
            <div class="metric-card">
                <div class="metric-label">Total Ukuran Asli</div>
                <div class="metric-value">{format_size(total_awal_off)}</div>
            </div>
            <div class="metric-card highlight">
                <div class="metric-label">Total Hasil Baru</div>
                <div class="metric-value">{format_size(total_akhir_off)}</div>
                <span class="badge-hemat">Hemat {total_hemat_off:.1f}%</span>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Dokumen</div>
                <div class="metric-value">{len(files_off)} File</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        zip_buf_off = io.BytesIO()
        with zipfile.ZipFile(zip_buf_off, 'w', zipfile.ZIP_DEFLATED) as z:
            for item in list_hasil_off:
                z.writestr(item["out_name"], item["bytes"])
        zip_bytes_off = zip_buf_off.getvalue()

        # Tombol Download ZIP (Memanggil hud_slot global)
        btn_zip_off = st.download_button(
            label=f"⬇️ DOWNLOAD SEMUA ({len(files_off)} DOKUMEN) - ZIP ({format_size(len(zip_bytes_off))})",
            data=zip_bytes_off,
            file_name="CompressPro_Office_Bundle.zip",
            mime="application/zip",
            use_container_width=True,
            key="btn_download_zip_off"
        )
        if btn_zip_off:
            show_download_loading(kategori="office", is_bundle=True)

        # Rincian Unduh Satuan (Juga Memanggil hud_slot global)
        with st.expander("📋 Rincian & Unduh Satuan Tiap Dokumen", expanded=True):
            for i, item in enumerate(list_hasil_off):
                item_hemat = ((item["awal"] - item["akhir"]) / item["awal"]) * 100 if item["awal"] > item["akhir"] else 0.0
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"**{item['name']}**")
                    st.caption(f"{format_size(item['awal'])} ➔ **{format_size(item['akhir'])}** (Hemat {item_hemat:.1f}%)")
                with c2:
                    btn_single_off = st.download_button(
                        label="⬇️ Unduh",
                        data=item["bytes"],
                        file_name=item["out_name"],
                        mime=item["mime"],
                        key=f"dl_single_off_{i}",
                        use_container_width=True
                    )
                    if btn_single_off:
                        show_download_loading(kategori="office", is_bundle=False, file_name=item["name"])
