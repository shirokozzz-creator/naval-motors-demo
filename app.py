import streamlit as st
import os

# ==========================================
# 1. 頁面全局設定
# ==========================================
st.set_page_config(
    page_title="Naval Motors 戰情室 | 數據驅動資產攔截",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 隱藏預設選單
hide_st_style = """<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# ==========================================
# 2. 戰情室標題
# ==========================================
st.markdown("<h1 style='text-align: center; color: #1E1E1E;'>Naval Motors 戰情室</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #4CAF50;'>【 認知錯殺與絕對套利 / CASE 001 】</h4>", unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# 3. 核心內容區 (圖片與文案雙欄)
# ==========================================
col_img, col_text = st.columns([1.2, 1])

with col_img:
    # 物理防呆機制：檢查圖片是否存在
    # 請確保這張圖片與 app.py 放在同一個 GitHub 資料夾的最外層
    img_filename = "Snipaste_2026-03-01_10-03-50.png"
    
    if os.path.exists(img_filename):
        st.image(img_filename, use_container_width=True)
    else:
        # 如果雲端抓不到圖片，顯示這段錯誤，而不會讓整個網頁死當
        st.error(f"⚠️ 系統警告：雲端找不到圖片檔案 `{img_filename}`。請執行長確認圖片已上傳至 GitHub，且副檔名大小寫完全一致。")

with col_text:
    st.markdown("### 物理除錯完畢：被掩蓋的完美資產")
    st.markdown("""
    市場總是為恐懼定價，而 Naval Motors 為實體數據買單。

    這是一台 **2022 Corolla Cross GR Hybrid**。在傳統市場，它因為「78,000 公里」與「營業退役」的標籤，遭到恐懼拋售。
    但工程學不看標籤，只看物理狀態。Naval Motors 透過情報攔截證實：
    
    * ✅ **Day-1 前已更換全新原廠 HV 大電池**
    * ✅ **四條全新輪胎**
    * ✅ **引擎缸壓與底盤件正常**
    
    最致命的耗材風險已被完全消滅。
    """)
    
    st.markdown("---")
    st.markdown("#### 📊 財務清算矩陣 (TCO Impact)")
    
    m1, m2, m3 = st.columns(3)
    m1.metric(label="終端無腦市價", value="71.0 萬")
    m2.metric(label="Naval 攔截總成本", value="57.9 萬")
    m3.metric(label="客戶實質淨套利", value="13.1 萬", delta="18.4% 暴擊", delta_color="normal")

# ==========================================
# 4. 漏斗收斂：強制行動呼籲 (CTA)
# ==========================================
st.markdown("---")
st.markdown("##### 拒絕傳統車商的資訊不對稱溢價。")
if st.button("🚀 支付 NT$ 3,000 啟動金，進入專屬戰情室", type="primary", use_container_width=True):
    st.success("（系統已記錄意向。正在為您串接支付閘道與委任合約簽署頁面...）")

st.divider()
st.caption("Disclaimer: 本戰報為 Naval Motors 實際執行之去識別化交易紀錄。高套利空間源自特定時空之市場認知錯殺。二手車資產存在個體差異。")

