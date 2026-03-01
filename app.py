import streamlit as st

# ==========================================
# 1. 頁面全局設定
# ==========================================
st.set_page_config(
    page_title="Naval Motors 戰情室 | 數據驅動資產攔截",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 隱藏 Streamlit 預設介面，增加專業度
hide_st_style = """<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# ==========================================
# 2. 戰情室標題與案例 (維持上一回合的展示)
# ==========================================
st.markdown("<h1 style='text-align: center; color: #1E1E1E;'>Naval Motors 戰情室</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #4CAF50;'>【 認知錯殺與絕對套利 / Case 001 】</h4>", unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# 3. 車輛展示區域
# ==========================================
st.markdown("### 🧮 實戰案例展示")
st.markdown("Naval Motors 代理人制度，透過「絕對透明」與「工程師級排雷」，為您在檸檬市場中建立「絕對防禦型資產」。")

# 建立四欄佈局來展示四款車型
col1, col2, col3, col4 = st.columns(4)

# 使用是用戶提供的圖片和相應文案

# 第 1 欄：Lexus NX (Lexus NX200)
with col1:
    # 確保圖片 Snipaste_2026-03-01_10-03-50.jpg 與程式同目錄
    st.image("Snipaste_2026-03-01_10-03-50.jpg", use_container_width=True)
    st.markdown("""
    **標的 A：Lexus NX200**
    > **工程排雷：** 引擎缸壓與變速箱模組全綠。
    > **財務期望：** 市場錯殺空間達 15%。
    """)

# 第 2 欄：Lexus CT (Lexus CT200h)
with col2:
    # 確保圖片 image_1.png 與程式同目錄
    st.image("image_1.png", use_container_width=True)
    st.markdown("""
    **標的 B：Lexus CT200h**
    > **工程排雷：** 原廠換過全新 HV 大電池。
    > **財務期望：** Day-1 總持有成本 (TCO) 淨套利 8 萬。
    """)

# 第 3 欄：Altis (Toyota Corolla, Altis)
with col3:
    # 確保圖片 image_2.png 與程式同目錄
    st.image("image_2.png", use_container_width=True)
    st.markdown("""
    **標的 C：Toyota Corolla, Altis**
    > **工程排雷：** 單一一手自用車。
    > **財務期望：** 終端零售價差達 12 萬。
    """)

# 第 4 欄：Corolla Cross (Toyota Corolla Cross)
with col4:
    # 確保圖片 image_4.png 與程式同目錄
    st.image("image_4.png", use_container_width=True)
    st.markdown("""
    **標的 D：Toyota Corolla Cross**
    > **工程排雷：** 經原廠 VIN 碼查核，保固實質有效。
    > **財務期望：** 攔截總成本低於市價 5 萬。
    """)

# ==========================================
# 4. 漏斗收斂：強制行動呼籲 (CTA)
# ==========================================
st.markdown("---")
st.markdown("### 🛑 拒絕資訊不對稱的剝削")
st.markdown("想要一份沒有盲點的資產檢驗報告與低於市價的總成本？您的 2 萬到 3 萬元顧問費，本質上是為了消除「怕被騙的焦慮」所支付的保險費（Risk Premium）。支付啟動金，讓 Naval Motors 接管你的購車風險。")

# 給客戶一點多巴胺
if st.button("🚀 支付 NT$ 3,000 啟動金，授權 Naval 幫我攔截資產", type="primary", use_container_width=True):
    st.balloons()
    st.success("（系統已記錄意向。正在為您串接藍新金流/綠界支付閘道與委任合約簽署頁面...）")

st.divider()
st.caption("Disclaimer: 本展示版僅含圖片與文案供測試之用。Naval Motors 承諾絕對透明的物理排雷與數據揭露，並不保證未來拍賣市場能完美複製相同之溢價比例。二手車資產存在個體差異。")
