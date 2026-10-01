from decimal import Decimal, ROUND_HALF_UP

import pandas as pd
import streamlit as st

# 1. Cấu hình
FILE_PATH = '271_ELC3020_ELC3020_1.xlsx'   # tên file Excel (phải trùng chính xác với tên file trên GitHub)
LECTURER = 'Đỗ Hoàng Thu'

st.set_page_config(page_title='Tra Cứu Điểm ELC3020', page_icon='🎓')


# 2. Đọc file Excel
@st.cache_data
def load_data(path):
    df = pd.read_excel(path)
    df.columns = [' '.join(str(c).split()) for c in df.columns]   # bỏ xuống dòng/khoảng trắng thừa
    return df


try:
    df = load_data(FILE_PATH)
except FileNotFoundError:
    st.error(f"Lỗi: Không tìm thấy file '{FILE_PATH}'. Vui lòng kiểm tra lại tên file trên GitHub.")
    st.stop()
except Exception as e:
    st.error(f'Lỗi khi đọc file Excel: {e}')
    st.stop()

# 3. Nhận diện cột
#    3 cột đầu: Lớp | MSSV | Họ Tên. Cột "Thành phần 1 (...)" là điểm tổng hợp.
#    Các cột còn lại ở giữa (A, B, C, D...) là các điểm thành phần, hiển thị đúng theo tên cột trong Excel.
COL_LOP, COL_MSV, COL_TEN = df.columns[0], df.columns[1], df.columns[2]
df[COL_MSV] = df[COL_MSV].astype(str).str.strip()

COL_TP1 = next((c for c in df.columns if c.lower().startswith('thành phần 1')), df.columns[-1])
SCORE_COLS = [c for c in df.columns[3:] if c != COL_TP1]


# 4. Hàm định dạng điểm
def fmt(v):
    if pd.isna(v):
        return '-'                      # ô trống (ví dụ không có điểm cộng)
    v = round(float(v), 3)
    return str(int(v)) if v.is_integer() else str(v)


def fmt_tp1(v):
    """Thành phần 1: luôn 1 chữ số thập phân, làm tròn lên khi .x5 (giống Excel)."""
    if pd.isna(v):
        return '-'
    d = Decimal(str(round(float(v), 6))).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    return str(d)


# 5. Hàm tra cứu
def lookup_scores(mssv_input):
    mssv_input = str(mssv_input).strip()
    result = df[df[COL_MSV] == mssv_input]
    if result.empty:
        return None
    row = result.iloc[0]
    scores = [(c, fmt(row[c]), False) for c in SCORE_COLS]
    scores.append((COL_TP1, fmt_tp1(row[COL_TP1]), True))
    return {'Họ và Tên': row[COL_TEN], 'Lớp': row[COL_LOP], 'Điểm số': scores}


# 6. Giao diện
st.title('🤖 Tra Cứu Điểm ELC3020')
st.markdown('---')

st.header('Nhập Mã Số Sinh Viên (MSSV)')
mssv_input = st.text_input('MSSV của bạn:', placeholder='Ví dụ: 221124008204')

if st.button('Tra Cứu Điểm', type='primary'):
    if mssv_input:
        with st.spinner('Đang tìm kiếm...'):
            data = lookup_scores(mssv_input)

        if data:
            st.success(f'✅ Tìm thấy: **{data["Họ và Tên"]}** - Lớp **{data["Lớp"]}**')
            st.subheader('Bảng Điểm Chi Tiết')

            # Bảng điểm, in đậm dòng Thành phần 1
            lines = ['| Thành Phần | Điểm |', '|:--|:--:|']
            for label, value, is_tp1 in data['Điểm số']:
                label = label.replace('*', '×')   # tránh dấu * bị hiểu nhầm là định dạng chữ
                if is_tp1:
                    lines.append(f'| **{label}** | **{value}** |')
                else:
                    lines.append(f'| {label} | {value} |')
            st.markdown('\n'.join(lines))
        else:
            st.error(f'❌ Không tìm thấy dữ liệu cho MSSV: **{mssv_input}**.')
    else:
        st.warning('⚠️ Vui lòng nhập Mã Số Sinh Viên.')

st.markdown('---')
st.caption(f'Giảng viên: {LECTURER}')
