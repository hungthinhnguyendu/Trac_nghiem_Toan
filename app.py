import streamlit as st
import json
import random

# TÙY CHỈNH GIAO DIỆN & MÀU SẮC
st.set_page_config(page_title="Khảo thí Toán Phước Thịnh", page_icon="🚀", layout="centered")
st.markdown("""
<style>
.stApp { background-color: #f4f9f9; }
.title-box {
    background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
    padding: 20px; border-radius: 15px; text-align: center;
    color: #1E3C72; font-family: 'Arial', sans-serif; box-shadow: 2px 4px 10px rgba(0,0,0,0.1); margin-bottom: 25px;
}
.cau-hoi { color: #d90429; font-size: 18px; font-weight: bold; margin-top: 20px; margin-bottom: 10px;}
.dap-an-dung { background-color: #d4edda; color: #155724; padding: 10px; border-left: 5px solid #28a745; margin-top: 10px; border-radius: 4px; font-weight: bold;}
div[data-testid="stFormSubmitButton"] > button {
    background-color: #FF4B4B; color: white; border-radius: 8px; font-weight: bold; width: 100%;
}
div[data-testid="stFormSubmitButton"] > button:hover { border: 2px solid #FF4B4B; color: #FF4B4B; background-color: white;}
</style>
""", unsafe_allow_html=True)

# ĐỌC DỮ LIỆU
@st.cache_data
def doc_du_lieu():
    try:
        with open("NGAN_HANG_JSON/ngan_hang_de.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except: return []

du_lieu_goc = doc_du_lieu()

# BẢNG ĐIỀU KHIỂN BÊN TRÁI (SIDEBAR)
st.sidebar.markdown("### ⚙️ BẢNG ĐIỀU KHIỂN")
sl_p1 = st.sidebar.number_input("Số câu Phần I", min_value=1, max_value=20, value=12)
sl_p2 = st.sidebar.number_input("Số câu Phần II", min_value=1, max_value=10, value=4)
sl_p3 = st.sidebar.number_input("Số câu Phần III", min_value=1, max_value=10, value=6)
hien_dap_an = st.sidebar.checkbox("Hiển thị đáp án sau khi nộp", value=True)

if st.sidebar.button("🔄 ÁP DỤNG & TẠO ĐỀ MỚI", type="primary"):
    st.session_state.pop('de_thi', None)
    st.session_state.nop_bai = False
    st.rerun()

# HÀM BỐC ĐỀ & XÁO TRỘN ĐÁP ÁN (Gắn A, B, C, D)
def tao_de_thi(ngan_hang, sl1, sl2, sl3):
    cay = {"Phan_1_Trac_Nghiem": {}, "Phan_2_Dung_Sai": {}, "Phan_3_Tra_Loi_Ngan": {}}
    for c in ngan_hang:
        loai = c.get("loai_cau")
        nhom = str(c.get("nhom", "1")).replace("Nhom_", "").replace("P1-N", "").replace("P2-N", "").replace("P3-N", "")
        if loai in cay:
            if nhom not in cay[loai]: cay[loai][nhom] = []
            cay[loai][nhom].append(c)
            
    de_thi = []
    # Hàm rút ngẫu nhiên và xáo trộn
    def rut_cau(loai_cau, so_luong, co_abcd=False):
        nhom_hien_co = list(cay[loai_cau].keys())
        nhom_chon = random.sample(nhom_hien_co, min(so_luong, len(nhom_hien_co)))
        cau_da_chon = []
        for n in nhom_chon:
            if cay[loai_cau][n]:
                cau = random.choice(cay[loai_cau][n]).copy()
                if 'phuong_an' in cau:
                    random.shuffle(cau['phuong_an']) # Đảo vị trí đáp án
                    if co_abcd:
                        chu_cai = ['A', 'B', 'C', 'D']
                        for idx, pa in enumerate(cau['phuong_an']):
                            if idx < 4: pa['nhan_hien_thi'] = f"{chu_cai[idx]}. {pa['noi_dung']}"
                    else:
                        chu_cai_thuong = ['a', 'b', 'c', 'd']
                        for idx, pa in enumerate(cau['phuong_an']):
                            if idx < 4: pa['nhan_hien_thi'] = f"{chu_cai_thuong[idx]}) {pa['noi_dung']}"
                cau_da_chon.append(cau)
        random.shuffle(cau_da_chon) # Đảo thứ tự câu hỏi
        return cau_da_chon

    de_thi.extend(rut_cau("Phan_1_Trac_Nghiem", sl1, co_abcd=True))
    de_thi.extend(rut_cau("Phan_2_Dung_Sai", sl2, co_abcd=False))
    de_thi.extend(rut_cau("Phan_3_Tra_Loi_Ngan", sl3, co_abcd=False))
    return de_thi

# LƯU TRẠNG THÁI ĐỀ THI
if not du_lieu_goc:
    st.error("Chưa có dữ liệu ngân hàng đề.")
    st.stop()

if 'de_thi' not in st.session_state:
    st.session_state.de_thi = tao_de_thi(du_lieu_goc, sl_p1, sl_p2, sl_p3)
    st.session_state.nop_bai = False

phan1 = [c for c in st.session_state.de_thi if c['loai_cau'] == 'Phan_1_Trac_Nghiem']
phan2 = [c for c in st.session_state.de_thi if c['loai_cau'] == 'Phan_2_Dung_Sai']
phan3 = [c for c in st.session_state.de_thi if c['loai_cau'] == 'Phan_3_Tra_Loi_Ngan']

# GIAO DIỆN CHÍNH
st.markdown('<div class="title-box"><h2>🚀 HỆ THỐNG TRẮC NGHIỆM TOÁN THPT</h2></div>', unsafe_allow_html=True)

with st.form("form_thi"):
    # PHẦN I
    if phan1: st.markdown("### PHẦN I. CÂU TRẮC NGHIỆM (Chọn 1 đáp án)")
    for i, cau in enumerate(phan1):
        st.markdown(f'<div class="cau-hoi">Câu {i+1}: {cau["de_bai"]}</div>', unsafe_allow_html=True)
        if cau.get('hinh_anh'): st.markdown(f'<img src="data:image/png;base64,{cau["hinh_anh"]}" width="350">', unsafe_allow_html=True)
        
        ds_pa = [p['nhan_hien_thi'] for p in cau['phuong_an']]
        st.radio("Chọn đáp án:", options=ds_pa, key=f"p1_{cau['id']}", index=None, label_visibility="collapsed")
        
        if st.session_state.nop_bai and hien_dap_an:
            dap_an_dung = next(p['nhan_hien_thi'] for p in cau['phuong_an'] if p['la_dap_an_dung'])
            st.markdown(f'<div class="dap-an-dung">✨ Đáp án đúng: {dap_an_dung}</div>', unsafe_allow_html=True)
        st.divider()

    # PHẦN II
    if phan2: st.markdown("### PHẦN II. CÂU TRẮC NGHIỆM ĐÚNG/SAI")
    for i, cau in enumerate(phan2):
        st.markdown(f'<div class="cau-hoi">Câu {i+1+len(phan1)}: {cau["de_bai"]}</div>', unsafe_allow_html=True)
        if cau.get('hinh_anh'): st.markdown(f'<img src="data:image/png;base64,{cau["hinh_anh"]}" width="350">', unsafe_allow_html=True)
        
        for j, y_hoi in enumerate(cau['phuong_an']):
            st.write(f"**{y_hoi['nhan_hien_thi']}**")
            st.radio("Đánh giá:", options=["Đúng", "Sai"], key=f"p2_{cau['id']}_{j}", index=None, horizontal=True, label_visibility="collapsed")
            
            if st.session_state.nop_bai and hien_dap_an:
                dung_sai_text = "Đúng" if y_hoi['la_dap_an_dung'] else "Sai"
                st.markdown(f'<div class="dap-an-dung">✨ Ý {y_hoi["nhan_hien_thi"][:2]} là mệnh đề: {dung_sai_text}</div>', unsafe_allow_html=True)
        st.divider()

    # PHẦN III
    if phan3: st.markdown("### PHẦN III. CÂU TRẢ LỜI NGẮN")
    for i, cau in enumerate(phan3):
        st.markdown(f'<div class="cau-hoi">Câu {i+1+len(phan1)+len(phan2)}: {cau["de_bai"]}</div>', unsafe_allow_html=True)
        if cau.get('hinh_anh'): st.markdown(f'<img src="data:image/png;base64,{cau["hinh_anh"]}" width="350">', unsafe_allow_html=True)
        
        st.text_input("Nhập đáp án của em (VD: 2,34):", key=f"p3_{cau['id']}")
        
        if st.session_state.nop_bai and hien_dap_an:
            st.markdown(f'<div class="dap-an-dung">✨ Đáp án đúng: {cau.get("dap_an_dung", "")}</div>', unsafe_allow_html=True)
        st.divider()

    btn_nop_bai = st.form_submit_button("NỘP BÀI")

# CHẤM ĐIỂM
if btn_nop_bai:
    tong_diem = 0.0
    diem_toi_da = len(phan1)*0.25 + len(phan2)*1.0 + len(phan3)*0.5
    
    for cau in phan1:
        da_chon = st.session_state.get(f"p1_{cau['id']}")
        da_dung = next((p['nhan_hien_thi'] for p in cau['phuong_an'] if p['la_dap_an_dung']), None)
        if da_chon == da_dung: tong_diem += 0.25
            
    for cau in phan2:
        so_y_dung = 0
        for j, p in enumerate(cau['phuong_an']):
            chon = st.session_state.get(f"p2_{cau['id']}_{j}")
            dung = "Đúng" if p['la_dap_an_dung'] else "Sai"
            if chon == dung: so_y_dung += 1
        if so_y_dung == 1: tong_diem += 0.1
        elif so_y_dung == 2: tong_diem += 0.25
        elif so_y_dung == 3: tong_diem += 0.5
        elif so_y_dung == 4: tong_diem += 1.0
            
    for cau in phan3:
        # Tự động thay thế dấu phẩy (,) thành dấu chấm (.) để khớp đáp án
        chon = str(st.session_state.get(f"p3_{cau['id']}", "")).strip().replace(",", ".")
        dung = str(cau.get('dap_an_dung', "")).strip().replace(",", ".")
        if chon == dung and chon != "": tong_diem += 0.5

    st.session_state.nop_bai = True
    st.rerun() # Tải lại trang để hiện đáp án

# HIỂN THỊ ĐIỂM TỔNG TỔNG KẾT
if st.session_state.nop_bai:
    diem_toi_da = len(phan1)*0.25 + len(phan2)*1.0 + len(phan3)*0.5
    st.markdown(f'<div style="background: #e2e3e5; color: #383d41; padding: 15px; border-radius: 10px; text-align: center; font-size: 24px; font-weight: bold;">🎯 ĐIỂM CỦA EM: {round(tong_diem, 2)} / {diem_toi_da}</div>', unsafe_allow_html=True)
    st.balloons()
