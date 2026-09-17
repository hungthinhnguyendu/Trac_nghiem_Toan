import streamlit as st
import streamlit.components.v1 as components
import json
import random
import os
import pandas as pd
from datetime import datetime
import re
import base64

st.set_page_config(page_title="Khảo Thí Toán Phước Thịnh", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #f4f9f9; }
.title-box {
    background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
    padding: 20px; border-radius: 15px; text-align: center;
    color: #1E3C72; font-family: 'Arial', sans-serif;
    box-shadow: 2px 4px 10px rgba(0,0,0,0.1); margin-bottom: 25px;
}
div.stButton > button:first-child {
    background-color: #FF4B4B; color: white; border-radius: 8px; font-weight: bold; border: 2px solid #FF4B4B; transition: 0.3s;
}
div.stButton > button:first-child:hover {
    background-color: white; color: #FF4B4B; border: 2px solid #FF4B4B;
}
/* Phóng to công thức Toán (KaTeX) một chút cho rõ, dễ nhìn hơn - CHỈ chỉnh cỡ chữ,
   KHÔNG đổi font-family của .katex (nếu ép font-family thường như Times/Arial lên
   toàn bộ .katex thì các ký hiệu Toán đặc biệt như căn, tích phân, dấu ngoặc giãn...
   sẽ vỡ hình vì các ký hiệu này cần đúng font riêng của KaTeX mới ghép hình chính xác). */
.katex { font-size: 1.15em !important; }

/* --- Banner cho từng phần --- */
.section-banner {
    padding: 14px 22px; border-radius: 12px; font-size: 1.35em; font-weight: 800;
    color: white; margin: 28px 0 16px 0; box-shadow: 2px 3px 10px rgba(0,0,0,0.15);
    letter-spacing: 0.3px;
}
.section-p1 { background: linear-gradient(135deg, #4facfe 0%, #00c9ff 100%); }
.section-p2 { background: linear-gradient(135deg, #f6a44a 0%, #fd6e6e 100%); }
.section-p3 { background: linear-gradient(135deg, #56ccae 0%, #6dd5ed 100%); }

/* --- Nhãn "Câu X:" --- */
.cau-nhan {
    display: inline-block; background-color: #ffd9ea; color: #1E3C72; font-weight: 800;
    padding: 5px 16px; border-radius: 20px; font-size: 1.08em; margin-right: 10px;
    box-shadow: 1px 2px 4px rgba(0,0,0,0.08);
}
.cau-noidung { font-size: 1.06em; }

/* --- Khối phát biểu Đúng/Sai (Phần II) --- */
.ds-statement {
    display: block;
    background: #eef6ff; border-left: 5px solid #1E88E5; padding: 10px 16px;
    border-radius: 10px; margin: 6px 0 2px 0; font-size: 1.02em;
}
.ds-nhan {
    display: inline-block; color: white; background-color: #1E88E5; font-weight: 800;
    font-size: 1.0em; margin-right: 8px; border-radius: 50%; width: 26px; height: 26px;
    text-align: center; line-height: 26px;
}

/* --- Khối đáp án A/B/C/D (Phần I) - cùng phong cách với ds-statement/ds-nhan --- */
.pa-statement {
    display: block;
    background: #eef6ff; border-left: 5px solid #1E3C72; padding: 10px 16px;
    border-radius: 10px; margin: 6px 0 2px 0; font-size: 1.04em;
}
.pa-nhan {
    display: inline-block; color: white; background-color: #1E3C72; font-weight: 800;
    font-size: 1.05em; margin-right: 10px; border-radius: 50%; width: 32px; height: 32px;
    text-align: center; line-height: 32px;
}

/* --- Nhãn "Đáp án:" ở Phần III --- */
.p3-nhan {
    color: #14976b; font-weight: 800; font-size: 1.05em;
}

/* --- Ô trả lời ngắn (4 ô, mỗi ô 1 ký tự) --- */
div[data-testid="stTextInput"] input[maxlength="1"] {
    text-align: center !important;
    font-size: 1.2em !important;
    font-weight: 800 !important;
    color: #1E3C72 !important;
    height: 42px !important;
    width: 42px !important;
    max-width: 42px !important;
    margin: 0 auto !important;
    display: block !important;
    border-radius: 8px !important;
    border: 2px solid #56ccae !important;
    background-color: #ffffff !important;
}

/* --- Đáp án trắc nghiệm to, dễ đọc --- */
.stRadio [role="radiogroup"] label { font-size: 1.06em; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-box"><h2>🚀 HỆ THỐNG TRẮC NGHIỆM TOÁN THPT</h2></div>', unsafe_allow_html=True)

THU_MUC_JSON = "NGAN_HANG_JSON"
if not os.path.exists(THU_MUC_JSON):
    os.makedirs(THU_MUC_JSON)


def _phong_to_ngoac_chua_phan_so(bieu_thuc):
    """Tự động đổi ( ) và [ ] bao quanh \\frac, \\dfrac, \\binom... thành
    \\left( \\right) / \\left[ \\right] để ngoặc giãn theo chiều cao phân số,
    tránh trường hợp ngoặc nhỏ không phủ hết phân số cao."""
    doi_ngoac = {'(': ')', '[': ']'}
    ky_hieu_lenh = {'(': r'\left(', ')': r'\right)', '[': r'\left[', ']': r'\right]'}
    ky_tu = list(bieu_thuc)
    stack_vi_tri, stack_loai, stack_co_phan_so = [], [], []
    i = 0
    while i < len(ky_tu):
        c = ky_tu[i]
        if c in '([':
            stack_vi_tri.append(i); stack_loai.append(c); stack_co_phan_so.append(False)
        elif c in ')]' and stack_loai and doi_ngoac.get(stack_loai[-1]) == c:
            vi_tri_mo = stack_vi_tri.pop(); loai_mo = stack_loai.pop(); co_phan_so = stack_co_phan_so.pop()
            if co_phan_so:
                ky_tu[vi_tri_mo] = ky_hieu_lenh[loai_mo]
                ky_tu[i] = ky_hieu_lenh[c]
                if stack_co_phan_so: stack_co_phan_so[-1] = True
        elif stack_co_phan_so and (bieu_thuc.startswith(r'\frac', i) or bieu_thuc.startswith(r'\dfrac', i) or bieu_thuc.startswith(r'\binom', i)):
            stack_co_phan_so[-1] = True
        i += 1
    return ''.join(ky_tu)


def lam_sach_latex(text):
    """Chuẩn hoá 1 đoạn văn bản còn sót cú pháp LaTeX (từ ngân hàng đề gói ex-test)
    thành Markdown + LaTeX mà Streamlit/KaTeX render đúng và đẹp."""
    if not isinstance(text, str): return text

    # \textbf{...}/\textit{...}/\emph{...} là lệnh định dạng chữ THƯỜNG (không phải
    # công thức Toán) -> phải đổi sang Markdown TRƯỚC khi dò tìm/tự bọc công thức
    # $...$ bên dưới, nếu không cả câu sẽ bị tưởng nhầm là công thức Toán.
    for _ in range(3):  # lặp vài lần để xử lý được cả trường hợp lồng nhau đơn giản
        text = re.sub(r'\\textbf\s*\{([^{}]*)\}', r'**\1**', text)
        text = re.sub(r'\\textit\s*\{([^{}]*)\}', r'*\1*', text)
        text = re.sub(r'\\emph\s*\{([^{}]*)\}', r'*\1*', text)
        text = re.sub(r'\\underline\s*\{([^{}]*)\}', r'<u>\1</u>', text)

    def _chuan_hoa_cong_thuc(noi_dung):
        noi_dung = noi_dung.strip()
        # Idempotent: nếu nội dung đã lỡ có \left/\right (do đề gốc tự gõ sẵn, hoặc
        # hàm này vô tình chạy nhiều lần) thì bỏ hết về ( ) trơn trước, rồi mới tự
        # thêm lại đúng 1 lớp \left\right.
        noi_dung = re.sub(r'(?:\\left)+(?=[\(\[])', '', noi_dung)
        noi_dung = re.sub(r'(?:\\right)+(?=[\)\]])', '', noi_dung)
        # \frac mặc định KaTeX hiển thị nhỏ (textstyle) khi đặt trong $...$, khác hẳn
        # bản PDF vốn đặt to rõ -> nâng lên \dfrac (displaystyle) để "đẹp" như trong tex.
        noi_dung = re.sub(r'\\frac(?![a-zA-Z])', r'\\dfrac', noi_dung)
        noi_dung = _phong_to_ngoac_chua_phan_so(noi_dung)
        return noi_dung

    if '$' in text:
        text = re.sub(r'\$([^\$]+)\$', lambda m: '$' + _chuan_hoa_cong_thuc(m.group(1)) + '$', text)
    elif re.search(r'\\[a-zA-Z]', text) and text.strip():
        # Nội dung có lệnh LaTeX (\frac, \infty, \left...) nhưng KHÔNG hề có dấu $
        # bao quanh (đề gốc gõ thiếu $) -> trình duyệt không nhận là công thức, hiện
        # nguyên chữ có gạch chéo ngược. Tự bọc $ lại.
        text = '$' + _chuan_hoa_cong_thuc(text) + '$'

    text = re.sub(r'\\vec\s*\{([A-Za-z]{2,})\}', r'\\overrightarrow{\1}', text)

    while r'\immini' in text:
        start_idx = text.find(r'\immini')
        first_brace = text.find('{', start_idx)
        if first_brace == -1: break

        do_sau, first_end = 0, -1
        for i in range(first_brace, len(text)):
            if text[i] == '{': do_sau += 1
            elif text[i] == '}':
                do_sau -= 1
                if do_sau == 0:
                    first_end = i
                    break
        if first_end == -1: break

        second_brace = text.find('{', first_end + 1)
        if second_brace != -1 and text[first_end+1 : second_brace].strip() == '':
            do_sau, second_end = 0, -1
            for i in range(second_brace, len(text)):
                if text[i] == '{': do_sau += 1
                elif text[i] == '}':
                    do_sau -= 1
                    if do_sau == 0:
                        second_end = i
                        break
            if second_end != -1:
                text = text[:start_idx] + text[first_brace+1:first_end] + text[second_end+1:]
                continue
        text = text[:start_idx] + text[first_brace+1:first_end] + text[first_end+1:]

    text = re.sub(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}', '', text, flags=re.DOTALL)
    text = re.sub(r'\\def\s*\\[a-zA-Z]+\s*\{.*?\}', '', text, flags=re.DOTALL)
    text = re.sub(r'\[scale=.*?\]', '', text)
    text = re.sub(r'^\s*\}\s*$', '', text, flags=re.MULTILINE)

    text = re.sub(r'\\begin\{tabular\}.*?\\end\{tabular\}', '\n*(Học sinh xem số liệu ở hình đính kèm bên dưới)*\n', text, flags=re.DOTALL)
    text = text.replace(r'\begin{center}', '').replace(r'\end{center}', '')
    text = text.replace(r'\begin{itemize}', '').replace(r'\end{itemize}', '')
    text = text.replace(r'\item', '\n- ')
    text = text.replace(r'\lq\lq', '"').replace(r'\rq\rq', '"')
    return text.strip()


def chuan_hoa_dap_an_ngan(text):
    """Chuẩn hoá đáp án trả lời ngắn trước khi so sánh, để không bị sai lệch
    vì: khoảng trắng thừa, dấu phẩy/chấm thập phân, hay ký tự LaTeX sót lại
    kiểu '3{,}74' hoặc có $...$ bao quanh."""
    if not isinstance(text, str): return ""
    text = text.strip()
    text = re.sub(r'\{([^{}])\}', r'\1', text)  # "3{,}74" -> "3,74"
    text = text.replace('$', '')
    text = text.replace(',', '.')
    text = re.sub(r'\s+', '', text)
    return text.strip()


def _dau_van_tay():
    return tuple((f, os.path.getmtime(os.path.join(THU_MUC_JSON, f))) for f in os.listdir(THU_MUC_JSON) if f.endswith('.json'))


@st.cache_data
def tai_du_lieu(_dau_vet):
    du_lieu = {"P1": [], "P2": [], "P3": []}
    for file_name in os.listdir(THU_MUC_JSON):
        if file_name.endswith('.json'):
            with open(os.path.join(THU_MUC_JSON, file_name), 'r', encoding='utf-8') as f:
                danh_sach = json.load(f)
                for cau in danh_sach:
                    loai = cau.get('loai_cau')
                    if loai == "Phan_1_Trac_Nghiem": du_lieu["P1"].append(cau)
                    elif loai == "Phan_2_Dung_Sai": du_lieu["P2"].append(cau)
                    elif loai == "Phan_3_Tra_Loi_Ngan": du_lieu["P3"].append(cau)
    return du_lieu


def hien_thi_hinh(hinh_anh_b64):
    """Hiển thị hình ảnh căn giữa và tự scale theo chiều rộng cột."""
    if hinh_anh_b64:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.image(base64.b64decode(hinh_anh_b64), use_container_width=True)


def hien_thi_nhan_cau(so_thu_tu, noi_dung):
    """Hiển thị nhãn 'Câu X:' nền hồng nhạt, chữ xanh dương đậm, cùng dòng với đề bài.
    Lưu ý: dùng <span> (không dùng <div>) để Streamlit vẫn nhận diện đây là đoạn
    Markdown thường và tiếp tục render công thức LaTeX $...$ bên trong noi_dung."""
    st.markdown(
        f'<span class="cau-nhan">Câu {so_thu_tu}:</span> '
        f'<span class="cau-noidung">{noi_dung}</span>',
        unsafe_allow_html=True
    )


def chon_cau_theo_ma_tran(kho_cau_hoi, so_cau_can_lay):
    """Bốc đều câu hỏi dựa trên các chủ đề (nhóm) được phân loại"""
    nhom_dict = {}
    for cau in kho_cau_hoi:
        cd = cau.get('chu_de', 'Chung')
        if cd not in nhom_dict: nhom_dict[cd] = []
        nhom_dict[cd].append(cau)

    de_thi = []
    danh_sach_chu_de = list(nhom_dict.keys())
    random.shuffle(danh_sach_chu_de)

    # Xoay vòng lấy mỗi chủ đề 1 câu cho đến khi đủ chỉ tiêu
    while len(de_thi) < so_cau_can_lay:
        da_them = False
        for cd in danh_sach_chu_de:
            if len(de_thi) >= so_cau_can_lay: break
            cau_kha_dung = [c for c in nhom_dict[cd] if c not in de_thi]
            if cau_kha_dung:
                de_thi.append(random.choice(cau_kha_dung))
                da_them = True
        if not da_them: break
    return de_thi


def tron_dap_an(cau):
    """Trả về 1 BẢN SAO của câu hỏi Phần I với 'phuong_an' đã xáo trộn ĐÚNG 1 LẦN.
    BẮT BUỘC gọi hàm này khi phát sinh đề (và lưu kết quả vào session_state), rồi
    dùng lại y nguyên khi hiển thị - KHÔNG được random.shuffle() lại lúc render.
    Lý do: Streamlit chạy lại (rerun) TOÀN BỘ script mỗi khi bấm "Nộp bài", nếu
    shuffle ngay trong vòng lặp render thì thứ tự A/B/C/D lúc chấm điểm (rerun sau
    khi nộp) sẽ khác với thứ tự học sinh nhìn thấy lúc chọn (rerun lúc làm bài)
    -> chấm sai be bét dù học sinh bấm đúng đáp án đang hiển thị trên màn hình."""
    cau_moi = dict(cau)
    phuong_an_moi = list(cau['phuong_an'])
    random.shuffle(phuong_an_moi)
    cau_moi['phuong_an'] = phuong_an_moi
    return cau_moi


if st.sidebar.button("🔄 Tải lại ngân hàng đề (xoá cache)", help="Bấm nếu bạn vừa cập nhật file JSON mà đề không đổi"):
    st.cache_data.clear()
    st.rerun()

ngan_hang = tai_du_lieu(_dau_van_tay())

st.sidebar.header("Cấu Hình Đề Kiểm Tra")
so_cau_p1 = st.sidebar.number_input(f"Phần I (Kho: {len(ngan_hang['P1'])})", min_value=0, value=min(12, len(ngan_hang['P1'])))
so_cau_p2 = st.sidebar.number_input(f"Phần II (Kho: {len(ngan_hang['P2'])})", min_value=0, value=min(4, len(ngan_hang['P2'])))
so_cau_p3 = st.sidebar.number_input(f"Phần III (Kho: {len(ngan_hang['P3'])})", min_value=0, value=min(6, len(ngan_hang['P3'])))

st.sidebar.markdown("---")
thoi_gian = st.sidebar.number_input("⏳ Thời gian làm bài (phút):", min_value=1, value=90)
xem_dap_an = st.sidebar.checkbox("Cho phép học sinh xem đáp án sau khi nộp", value=True)

if st.sidebar.button("Phát Sinh Mã Đề"):
    cau_p1 = [tron_dap_an(c) for c in chon_cau_theo_ma_tran(ngan_hang['P1'], so_cau_p1)]
    st.session_state['de_thi'] = {
        'P1': cau_p1,
        'P2': chon_cau_theo_ma_tran(ngan_hang['P2'], so_cau_p2),
        'P3': chon_cau_theo_ma_tran(ngan_hang['P3'], so_cau_p3)
    }
    st.session_state['thoi_gian_lam_bai'] = thoi_gian
    st.session_state['xem_dap_an'] = xem_dap_an

if 'de_thi' in st.session_state and sum(len(v) for v in st.session_state['de_thi'].values()) > 0:
    st.title("ĐỀ KIỂM TRA MÔN TOÁN THPT")

    # Đồng hồ đếm ngược
    timer_html = f"""
    <div style="font-family: Arial; font-size: 24px; color: #d9534f; font-weight: bold; text-align: center; border: 2px solid #d9534f; padding: 10px; border-radius: 8px; background-color: #fdf2f2; width: 220px; margin: 0 auto;">
        ⏳ <span id="time">{st.session_state['thoi_gian_lam_bai']}:00</span>
    </div>
    <script>
        var time = {st.session_state['thoi_gian_lam_bai'] * 60};
        var timer = setInterval(function() {{
            time--;
            var m = Math.floor(time / 60);
            var s = time % 60;
            document.getElementById("time").innerHTML = (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s);
            if (time <= 0) {{
                clearInterval(timer);
                document.getElementById("time").innerHTML = "HẾT GIỜ!";
            }}
        }}, 1000);
    </script>
    """
    components.html(timer_html, height=80)

    # Bắt đầu khu vực chọn thông tin học sinh
    col1, col2 = st.columns([1, 2]) # Cột tên rộng hơn cột lớp một chút
    
    # Đọc danh sách từ file Excel thầy đã chuẩn bị
    try:
        df_ds = pd.read_excel("DanhSachHocSinh.xlsx")
        # Lấy danh sách các lớp (loại bỏ trùng lặp)
        danh_sach_lop = df_ds['Lớp'].dropna().unique().tolist()
    except Exception:
        st.error("⚠️ Hệ thống chưa tìm thấy file DanhSachHocSinh.xlsx")
        danh_sach_lop = []
        df_ds = pd.DataFrame(columns=['Lớp', 'Họ Tên'])

    with col1: 
        lop = st.selectbox("Lớp:", options=danh_sach_lop, index=None, placeholder="-- Chọn lớp --")
        
    with col2: 
        # Tự động lọc danh sách học sinh theo lớp vừa chọn
        if lop:
            danh_sach_ten = df_ds[df_ds['Lớp'] == lop]['Họ Tên'].dropna().tolist()
        else:
            danh_sach_ten = []
            
        ho_ten = st.selectbox("Họ và Tên học sinh:", options=danh_sach_ten, index=None, placeholder="-- Vui lòng chọn Lớp trước --")
        
    st.markdown("---")

    with st.form(key='form_lam_bai'):
        dap_an_hoc_sinh = {}
        diem_so = 0
        chi_tiet_cham_diem = {"P1": [], "P2": [], "P3": []}

        if st.session_state['de_thi']['P1']:
            st.markdown('<div class="section-banner section-p1">📘 PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn</div>', unsafe_allow_html=True)
            for i, cau in enumerate(st.session_state['de_thi']['P1']):
                hien_thi_nhan_cau(i+1, lam_sach_latex(cau['de_bai']))
                hien_thi_hinh(cau.get('hinh_anh'))

                phuong_an = [lam_sach_latex(pa['noi_dung']) for pa in cau['phuong_an']]
                nhan_vong_tron = ['A', 'B', 'C', 'D']

                for idx, noi_dung_pa in enumerate(phuong_an):
                    st.markdown(
                        f'<span class="pa-statement"><span class="pa-nhan">{nhan_vong_tron[idx]}</span>'
                        f'{noi_dung_pa}</span>',
                        unsafe_allow_html=True
                    )

                chu_cai_chon = st.radio(
                    "Chọn đáp án:", nhan_vong_tron[:len(phuong_an)],
                    key=f"p1_{cau['id']}", index=None, horizontal=True
                )
                dap_an_hoc_sinh[cau['id']] = (
                    phuong_an[nhan_vong_tron.index(chu_cai_chon)] if chu_cai_chon else None
                )
                st.markdown("---")

        if st.session_state['de_thi']['P2']:
            st.markdown('<div class="section-banner section-p2">📙 PHẦN II. Câu trắc nghiệm đúng sai</div>', unsafe_allow_html=True)
            for i, cau in enumerate(st.session_state['de_thi']['P2']):
                hien_thi_nhan_cau(i+1, lam_sach_latex(cau['de_bai']))
                hien_thi_hinh(cau.get('hinh_anh'))

                dap_an_hoc_sinh[cau['id']] = []
                for j, pa in enumerate(cau['phuong_an']):
                    nhan_y = ['ⓐ', 'ⓑ', 'ⓒ', 'ⓓ'][j]
                    st.markdown(
                        f'<span class="ds-statement"><span class="ds-nhan">{nhan_y}</span>'
                        f'{lam_sach_latex(pa["noi_dung"])}</span>',
                        unsafe_allow_html=True
                    )
                    lua_chon = st.radio(
                        f"Chọn Đúng/Sai cho ý {nhan_y}:", ["Đúng", "Sai"],
                        key=f"p2_{cau['id']}_{j}", index=None, horizontal=True,
                        label_visibility="collapsed"
                    )
                    dap_an_hoc_sinh[cau['id']].append(lua_chon)
                st.markdown("---")

        if st.session_state['de_thi']['P3']:
            st.markdown('<div class="section-banner section-p3">📗 PHẦN III. Câu trắc nghiệm trả lời ngắn</div>', unsafe_allow_html=True)
            for i, cau in enumerate(st.session_state['de_thi']['P3']):
                hien_thi_nhan_cau(i+1, lam_sach_latex(cau['de_bai']))
                hien_thi_hinh(cau.get('hinh_anh'))

                st.markdown('<span class="p3-nhan">Đáp án:</span>', unsafe_allow_html=True)
                o1, o2, o3, o4, _ = st.columns([1, 1, 1, 1, 4])
                ky_tu = []
                for idx, cot in enumerate([o1, o2, o3, o4]):
                    with cot:
                        ky_tu.append(
                            st.text_input(f"ô {idx+1}", key=f"p3_{cau['id']}_o{idx}",
                                          max_chars=1, label_visibility="collapsed")
                        )
                dap_an_hoc_sinh[cau['id']] = "".join(ky_tu)
                st.markdown("---")

        submit = st.form_submit_button("Nộp bài")

    # Xử lý chấm điểm và thông báo kết quả
    if submit:
        if not ho_ten or not lop:
            st.error("Vui lòng nhập đầy đủ Họ tên và Lớp!")
        else:
            for cau in st.session_state['de_thi']['P1']:
                da_dung = next(pa['noi_dung'] for pa in cau['phuong_an'] if pa['la_dap_an_dung'])
                sv_chon = dap_an_hoc_sinh[cau['id']]
                if sv_chon == lam_sach_latex(da_dung):
                    diem_so += 0.25
                    chi_tiet_cham_diem["P1"].append((True, sv_chon, da_dung))
                else:
                    chi_tiet_cham_diem["P1"].append((False, sv_chon, da_dung))

            for cau in st.session_state['de_thi']['P2']:
                so_y_dung = 0
                y_chi_tiet = []
                for j, pa in enumerate(cau['phuong_an']):
                    da_dung = "Đúng" if pa['la_dap_an_dung'] else "Sai"
                    sv_chon = dap_an_hoc_sinh[cau['id']][j]
                    if sv_chon == da_dung:
                        so_y_dung += 1
                        y_chi_tiet.append((True, sv_chon, da_dung))
                    else:
                        y_chi_tiet.append((False, sv_chon, da_dung))

                if so_y_dung == 4: diem_so += 1
                elif so_y_dung == 3: diem_so += 0.5
                elif so_y_dung == 2: diem_so += 0.25
                elif so_y_dung == 1: diem_so += 0.1
                chi_tiet_cham_diem["P2"].append((so_y_dung, y_chi_tiet))

            for cau in st.session_state['de_thi']['P3']:
                sv_chon = chuan_hoa_dap_an_ngan(dap_an_hoc_sinh[cau['id']])
                da_dung = chuan_hoa_dap_an_ngan(cau['dap_an_dung'])
                if sv_chon == da_dung:
                    diem_so += 0.5
                    chi_tiet_cham_diem["P3"].append((True, sv_chon, da_dung))
                else:
                    chi_tiet_cham_diem["P3"].append((False, sv_chon, da_dung))

            st.success(f"Học sinh {ho_ten} đã hoàn thành. Điểm tổng cộng: {diem_so:.2f} điểm")

            # Ghi file Excel
            file_excel = "Bang_Diem_Toan.xlsx"
            df_moi = pd.DataFrame([{"Thời gian": datetime.now().strftime("%d/%m/%Y %H:%M"), "Họ tên": ho_ten, "Lớp": lop, "Điểm": diem_so}])
            if os.path.exists(file_excel):
                df_tong = pd.concat([pd.read_excel(file_excel), df_moi], ignore_index=True)
            else:
                df_tong = df_moi
            df_tong.to_excel(file_excel, index=False)

            # Hiển thị đáp án nếu giáo viên cho phép
            if st.session_state['xem_dap_an']:
                with st.expander("📖 XEM CHI TIẾT ĐÁP ÁN TỪNG CÂU", expanded=True):
                    st.markdown("**PHẦN I**")
                    for i, kq in enumerate(chi_tiet_cham_diem["P1"]):
                        if kq[0]: st.success(f"Câu {i+1}: Chính xác (Đáp án: {kq[2]})")
                        else: st.error(f"Câu {i+1}: Sai (Bạn chọn: {kq[1]} | Đáp án đúng: {kq[2]})")

                    st.markdown("**PHẦN II**")
                    for i, kq in enumerate(chi_tiet_cham_diem["P2"]):
                        st.info(f"Câu {i+1}: Bạn đúng {kq[0]}/4 ý")
                        for j, y_kq in enumerate(kq[1]):
                            nhan = ['a)', 'b)', 'c)', 'd)'][j]
                            if y_kq[0]: st.success(f"Ý {nhan} Chính xác (Đáp án: {y_kq[2]})")
                            else: st.error(f"Ý {nhan} Sai (Bạn chọn: {y_kq[1]} | Đáp án đúng: {y_kq[2]})")

                    st.markdown("**PHẦN III**")
                    for i, kq in enumerate(chi_tiet_cham_diem["P3"]):
                        if kq[0]: st.success(f"Câu {i+1}: Chính xác (Đáp án: {kq[2]})")
                        else: st.error(f"Câu {i+1}: Sai (Bạn nhập: {kq[1]} | Đáp án đúng: {kq[2]})")
