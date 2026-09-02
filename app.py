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

THU_MUC_JSON = "NGAN_HANG_JSON"
if not os.path.exists(THU_MUC_JSON):
    os.makedirs(THU_MUC_JSON)

def lam_sach_latex(text):
    if not isinstance(text, str): return text
    text = re.sub(r'\$([^\$]+)\$', lambda m: '$' + m.group(1).strip() + '$', text)
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

def _dau_van_tay_thu_muc_json():
    """Tạo 1 'dấu vân tay' (tên file + thời gian sửa đổi) của toàn bộ thư mục
    NGAN_HANG_JSON. Dùng làm khoá cache: hễ có file JSON nào bị thay/thêm/xoá,
    dấu vân tay này đổi -> Streamlit tự biết cache đã cũ và nạp lại từ đĩa,
    KHÔNG cần bạn phải tắt hẳn server hay xoá cache tay nữa."""
    dau_vet = []
    for file_name in sorted(os.listdir(THU_MUC_JSON)):
        if file_name.endswith('.json'):
            duong_dan = os.path.join(THU_MUC_JSON, file_name)
            dau_vet.append((file_name, os.path.getmtime(duong_dan)))
    return tuple(dau_vet)


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


@st.cache_data
def tai_du_lieu(_dau_vet):
    du_lieu = {"Phan_1_Trac_Nghiem": [], "Phan_2_Dung_Sai": [], "Phan_3_Tra_Loi_Ngan": []}
    for file_name in os.listdir(THU_MUC_JSON):
        if file_name.endswith('.json'):
            with open(os.path.join(THU_MUC_JSON, file_name), 'r', encoding='utf-8') as f:
                danh_sach = json.load(f)
                for cau in danh_sach:
                    if cau['loai_cau'] in du_lieu:
                        du_lieu[cau['loai_cau']].append(cau)
    return du_lieu

if st.sidebar.button("🔄 Tải lại ngân hàng đề (xoá cache)", help="Bấm nếu bạn vừa cập nhật file JSON mà đề không đổi"):
    st.cache_data.clear()
    st.rerun()

ngan_hang = tai_du_lieu(_dau_van_tay_thu_muc_json())

st.sidebar.header("Cấu Hình Đề Kiểm Tra")
so_cau_p1 = st.sidebar.number_input(f"Phần I (Kho: {len(ngan_hang['Phan_1_Trac_Nghiem'])})", min_value=0, value=12)
so_cau_p2 = st.sidebar.number_input(f"Phần II (Kho: {len(ngan_hang['Phan_2_Dung_Sai'])})", min_value=0, value=4)
so_cau_p3 = st.sidebar.number_input(f"Phần III (Kho: {len(ngan_hang['Phan_3_Tra_Loi_Ngan'])})", min_value=0, value=6)

st.sidebar.markdown("---")
thoi_gian = st.sidebar.number_input("⏳ Thời gian làm bài (phút):", min_value=1, value=90)
xem_dap_an = st.sidebar.checkbox("Cho phép học sinh xem đáp án sau khi nộp", value=True)

if st.sidebar.button("Phát Sinh Mã Đề"):
    st.session_state['de_thi'] = {
        'P1': random.sample(ngan_hang['Phan_1_Trac_Nghiem'], min(so_cau_p1, len(ngan_hang['Phan_1_Trac_Nghiem']))),
        'P2': random.sample(ngan_hang['Phan_2_Dung_Sai'], min(so_cau_p2, len(ngan_hang['Phan_2_Dung_Sai']))),
        'P3': random.sample(ngan_hang['Phan_3_Tra_Loi_Ngan'], min(so_cau_p3, len(ngan_hang['Phan_3_Tra_Loi_Ngan'])))
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
    
    col1, col2 = st.columns(2)
    with col1: ho_ten = st.text_input("Họ và Tên học sinh:")
    with col2: lop = st.text_input("Lớp:")
    st.markdown("---")
    
    with st.form(key='form_lam_bai'):
        dap_an_hoc_sinh = {}
        diem_so = 0
        
        st.header("PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.")
        cau_hien_tai = 1
        for cau in st.session_state['de_thi']['P1']:
            st.markdown(f"**Câu {cau_hien_tai}:** {lam_sach_latex(cau['de_bai'])}")
            
            # Giải mã Base64 và hiển thị ảnh trực tiếp từ JSON
            if cau.get('hinh_anh'):
                st.image(base64.b64decode(cau['hinh_anh']), width=500)
                
            phuong_an = [lam_sach_latex(pa['noi_dung']) for pa in cau['phuong_an']]
            random.shuffle(phuong_an)
            dap_an_hoc_sinh[cau['id']] = st.radio("Chọn đáp án:", phuong_an, key=f"p1_{cau['id']}", index=None)
            cau_hien_tai += 1
            st.markdown("---")
            
        st.header("PHẦN II. Câu trắc nghiệm đúng sai.")
        cau_hien_tai = 1
        for cau in st.session_state['de_thi']['P2']:
            st.markdown(f"**Câu {cau_hien_tai}:** {lam_sach_latex(cau['de_bai'])}")
            
            if cau.get('hinh_anh'):
                st.image(base64.b64decode(cau['hinh_anh']), width=500)
                
            dap_an_hoc_sinh[cau['id']] = []
            for j, pa in enumerate(cau['phuong_an']):
                nhan_y = ['a)', 'b)', 'c)', 'd)'][j]
                st.write(f"{nhan_y} {lam_sach_latex(pa['noi_dung'])}")
                lua_chon = st.radio(f"Chọn Đúng/Sai cho ý {nhan_y}:", ["Đúng", "Sai"], key=f"p2_{cau['id']}_{j}", index=None, horizontal=True)
                dap_an_hoc_sinh[cau['id']].append(lua_chon)
            cau_hien_tai += 1
            st.markdown("---")
            
        st.header("PHẦN III. Câu trắc nghiệm trả lời ngắn.")
        cau_hien_tai = 1
        for cau in st.session_state['de_thi']['P3']:
            st.markdown(f"**Câu {cau_hien_tai}:** {lam_sach_latex(cau['de_bai'])}")
            
            if cau.get('hinh_anh'):
                st.image(base64.b64decode(cau['hinh_anh']), width=500)
                
            dap_an_hoc_sinh[cau['id']] = st.text_input("Nhập đáp án:", key=f"p3_{cau['id']}")
            cau_hien_tai += 1
            st.markdown("---")
            
        submit = st.form_submit_button("Nộp bài")

    # Xử lý chấm điểm và thông báo kết quả
    if submit:
        if not ho_ten or not lop:
            st.error("Vui lòng nhập đầy đủ Họ tên và Lớp!")
        else:
            chi_tiet_cham_diem = {"P1": [], "P2": [], "P3": []}
            
            for cau in st.session_state['de_thi']['P1']:
                dap_an_dung = lam_sach_latex(next(pa['noi_dung'] for pa in cau['phuong_an'] if pa['la_dap_an_dung']))
                sv_chon = dap_an_hoc_sinh[cau['id']]
                if sv_chon == dap_an_dung:
                    diem_so += 0.25
                    chi_tiet_cham_diem["P1"].append((True, sv_chon, dap_an_dung))
                else:
                    chi_tiet_cham_diem["P1"].append((False, sv_chon, dap_an_dung))
                    
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