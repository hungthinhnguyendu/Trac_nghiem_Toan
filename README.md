[app.py](https://github.com/user-attachments/files/31783546/app.py)
import streamlit as st
import json
import random
import base64

# 1. CẤU HÌNH GIAO DIỆN & CSS (Màu sắc, nút bấm, nền)
st.set_page_config(page_title="Khảo thí Toán THPT", page_icon="🚀", layout="centered")

st.markdown("""
<style>
.stApp { background-color: #f4f9f9; }
.title-box {
    background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    color: #1E3C72;
    font-family: 'Arial', sans-serif;
    box-shadow: 2px 4px 10px rgba(0,0,0,0.1);
    margin-bottom: 25px;
}
div[data-testid="stFormSubmitButton"] > button {
    background-color: #FF4B4B; color: white; border-radius: 8px;
    font-weight: bold; border: 2px solid #FF4B4B; transition: 0.3s; width: 100%;
}
div[data-testid="stFormSubmitButton"] > button:hover {
    background-color: white; color: #FF4B4B; border: 2px solid #FF4B4B;
}
.diem-box {
    background: #d4edda; color: #155724; padding: 15px;
    border-radius: 10px; text-align: center; font-size: 24px; font-weight: bold;
    margin-bottom: 20px; border: 1px solid #c3e6cb;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-box"><h2>🚀 HỆ THỐNG TRẮC NGHIỆM TOÁN THPT</h2></div>', unsafe_allow_html=True)

# 2. HÀM ĐỌC VÀ BỐC ĐỀ TỪ CÂY DỮ LIỆU
@st.cache_data
def doc_du_lieu():
    try:
        with open("NGAN_HANG_JSON/ngan_hang_de.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return []

def bieu_dien_de_thi_ngau_nhien(ngan_hang_json):
    # Phân rã dữ liệu vào cây thư mục dựa trên loai_cau và thuộc tính nhom
    cay_thu_muc = {"Phan_1_Trac_Nghiem": {}, "Phan_2_Dung_Sai": {}, "Phan_3_Tra_Loi_Ngan": {}}
    for cau in ngan_hang_json:
        loai = cau.get("loai_cau")
        nhom = str(cau.get("nhom", "1")).replace("Nhom_", "").replace("P1-N", "").replace("P2-N", "").replace("P3-N", "")
        if loai in cay_thu_muc:
            if nhom not in cay_thu_muc[loai]: cay_thu_muc[loai][nhom] = []
            cay_thu_muc[loai][nhom].append(cau)
            
    de_thi_ca_nhan = []
    # Rút chính xác 1 câu ngẫu nhiên từ mỗi nhóm (đã sắp xếp thứ tự nhóm 1->12)
    for loai in ["Phan_1_Trac_Nghiem", "Phan_2_Dung_Sai", "Phan_3_Tra_Loi_Ngan"]:
        cac_nhom = sorted(cay_thu_muc[loai].keys(), key=lambda x: int(x) if x.isdigit() else x)
        for nhom in cac_nhom:
            if cay_thu_muc[loai][nhom]:
                de_thi_ca_nhan.append(random.choice(cay_thu_muc[loai][nhom]))
    return de_thi_ca_nhan

# 3. QUẢN LÝ TRẠNG THÁI (Khóa đề thi không bị đổi khi click chọn đáp án)
du_lieu_goc = doc_du_lieu()
if not du_lieu_goc:
    st.error("Chưa tìm thấy dữ liệu. Thầy kiểm tra lại thư mục NGAN_HANG_JSON nhé!")
    st.stop()

if 'de_thi' not in st.session_state or st.session_state.get('nop_bai', False):
    st.session_state.de_thi = bieu_dien_de_thi_ngau_nhien(du_lieu_goc)
    st.session_state.nop_bai = False

phan1 = [c for c in st.session_state.de_thi if c['loai_cau'] == 'Phan_1_Trac_Nghiem']
phan2 = [c for c in st.session_state.de_thi if c['loai_cau'] == 'Phan_2_Dung_Sai']
phan3 = [c for c in st.session_state.de_thi if c['loai_cau'] == 'Phan_3_Tra_Loi_Ngan']

# 4. GIAO DIỆN LÀM BÀI
with st.form("form_thi"):
    # PHẦN I
    st.markdown("### PHẦN I. CÂU TRẮC NGHIỆM NHIỀU PHƯƠNG ÁN LỰA CHỌN")
    for i, cau in enumerate(phan1):
        st.markdown(f"**Câu {i+1}:** {cau['de_bai']}")
        if cau.get('hinh_anh'):
            st.markdown(f'<img src="data:image/png;base64,{cau["hinh_anh"]}" width="300">', unsafe_allow_html=True)
        ds_phuong_an = [p['noi_dung'] for p in cau['phuong_an']]
        st.radio("Chọn 1 đáp án:", options=ds_phuong_an, key=f"p1_{cau['id']}", index=None, label_visibility="collapsed")
        st.divider()

    # PHẦN II
    st.markdown("### PHẦN II. CÂU TRẮC NGHIỆM ĐÚNG/SAI")
    for i, cau in enumerate(phan2):
        st.markdown(f"**Câu {i+1}:** {cau['de_bai']}")
        if cau.get('hinh_anh'):
            st.markdown(f'<img src="data:image/png;base64,{cau["hinh_anh"]}" width="300">', unsafe_allow_html=True)
        for j, y_hoi in enumerate(cau['phuong_an']):
            st.markdown(f"- {y_hoi['noi_dung']}")
            st.radio("Đánh giá:", options=["Đúng", "Sai"], key=f"p2_{cau['id']}_{j}", index=None, horizontal=True)
        st.divider()

    # PHẦN III
    st.markdown("### PHẦN III. CÂU TRẮC NGHIỆM TRẢ LỜI NGẮN")
    for i, cau in enumerate(phan3):
        st.markdown(f"**Câu {i+1}:** {cau['de_bai']}")
        if cau.get('hinh_anh'):
            st.markdown(f'<img src="data:image/png;base64,{cau["hinh_anh"]}" width="300">', unsafe_allow_html=True)
        st.text_input("Nhập đáp án của em:", key=f"p3_{cau['id']}")
        st.divider()

    btn_nop_bai = st.form_submit_button("NỘP BÀI")

# 5. THUẬT TOÁN CHẤM ĐIỂM (Cấu trúc 2025: Tối đa 10 điểm)
if btn_nop_bai:
    tong_diem = 0.0
    
    # Chấm Phần I (0.25đ / câu)
    for cau in phan1:
        da_chon = st.session_state.get(f"p1_{cau['id']}")
        da_dung = next((p['noi_dung'] for p in cau['phuong_an'] if p['la_dap_an_dung']), None)
        if da_chon == da_dung: tong_diem += 0.25
            
    # Chấm Phần II (1 ý = 0.1đ; 2 ý = 0.25đ; 3 ý = 0.5đ; 4 ý = 1.0đ)
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
            
    # Chấm Phần III (0.5đ / câu)
    for cau in phan3:
        chon = str(st.session_state.get(f"p3_{cau['id']}", "")).strip().lower()
        dung = str(cau.get('dap_an_dung', "")).strip().lower()
        if chon == dung and chon != "": tong_diem += 0.5

    # Đẩy kết quả lên đầu màn hình
    st.session_state.nop_bai = True
    st.markdown(f'<div class="diem-box">🎯 ĐIỂM CỦA EM: {round(tong_diem, 2)} / 10</div>', unsafe_allow_html=True)
    
    if tong_diem >= 8.0:
        st.balloons()
        st.success("Tuyệt vời! Xuất sắc lắm! 🏆")
    elif tong_diem >= 5.0:
        st.info("Khá lắm, cố gắng phát huy nhé! 💡")
    else:
        st.error("Cần ôn tập kỹ hơn các dạng toán này em nhé. Đừng nản chí! 💪")
        
    if st.button("LÀM MÃ ĐỀ MỚI 🔄"):
        st.rerun()
