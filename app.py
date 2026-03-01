import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 1. 頁面全局設定
# ==========================================
st.set_page_config(
    page_title="Naval Motors 戰情室 | 數據驅動資產攔截",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

hide_st_style = """<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# ==========================================
# 2. 戰略緩存：讀取情報資產 (CSV)
# ==========================================
# 使用 @st.cache_data 裝飾器，確保資料只讀取一次，節省伺服器運算資源
@st.cache_data
def load_data():
    try:
        # 嘗試讀取您的資料庫
        df = pd.read_csv("clean_toyota_data.csv")
        return df
    except FileNotFoundError:
        # 防呆機制：如果雲端找不到 CSV，生成備用測試數據庫，防止網站崩潰
        st.warning("⚠️ 系統警告：偵測不到 clean_toyota_data.csv，已自動切換為備用戰術數據庫。")
        data = {
            'Car_Model': ['Corolla Cross Hybrid', 'NX200', 'CT200h', 'Altis', 'Camry Hybrid'],
            'Market_Price_Avg': [710000, 920000, 440000, 540000, 650000],
            'Battery_Risk_Cost': [45000, 0, 45000, 0, 50000], # 大電池隱藏 CapEx
            'Tire_Cost': [12000, 16000, 12000, 10000, 14000],
            'Major_Service_Cost': [8000, 12000, 8000, 6000, 10000]
        }
        return pd.DataFrame(data)

df = load_data()

# ==========================================
# 3. 頁面標題與首發案例 (維持上一回合的展示)
# ==========================================
st.markdown("<h1 style='text-align: center; color: #1E1E1E;'>Naval Motors 戰情室</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #4CAF50;'>【 數據過濾雜訊，紀律決定套利 】</h4>", unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# 4. 核心武器：TCO 殘酷試算器 (The Reality Check)
# ==========================================
st.markdown("### 🧮 隱藏成本掃描：TCO 殘酷試算器")
st.markdown("傳統車商只讓你看到**「車價」**，Naval Motors 讓你直面資產的**「總持有成本 (Total Cost of Ownership)」**。")

# 建立兩欄佈局：左邊讓客戶操作，右邊出報表
col_input, col_output = st.columns([1, 1.5])

with col_input:
    st.markdown("##### 1. 輸入您的鎖定標的")
    # 讓客戶從您的 CSV 資料庫中選擇車型
    selected_car = st.selectbox("選擇車型 (Model)：", df['Car_Model'].unique())
    
    # 獲取該車型的數據
    car_data = df[df['Car_Model'] == selected_car].iloc[0]
    market_price = car_data['Market_Price_Avg']
    
    st.markdown("##### 2. 設定您的心理預期")
    expected_years = st.slider("預計持有年限 (年)：", 1, 10, 5)
    
    # 計算隱藏成本 (OPEX + 尾端風險 CapEx)
    hidden_cost = car_data['Battery_Risk_Cost'] + car_data['Tire_Cost'] + car_data['Major_Service_Cost']

with col_output:
    st.markdown("##### 📊 5 年期實體財務清算矩陣")
    
    # 用極端對比的圖表顯示：表面車價 vs 實際總噴錢
    total_cost = market_price + hidden_cost
    
    st.error(f"⚠️ 傳統車商不會告訴你的真相：這台車的隱藏整備與尾端風險金高達 **NT$ {hidden_cost:,.0f}**")
    
    m1, m2 = st.columns(2)
    m1.metric(label="表面終端均價", value=f"NT$ {market_price:,.0f}")
    m2.metric(label="真實總持有成本 (TCO)", value=f"NT$ {total_cost:,.0f}", delta=f"+{hidden_cost:,.0f} 隱藏耗材", delta_color="inverse")
    
    st.markdown("""
    > **工程學邏輯：** 如果你用市價買入，且沒有在 Day-1 檢查大電池模組電壓與耗材狀態，這筆隱藏成本將在未來 5 年內無情擊穿你的現金流。
    """)

# ==========================================
# 5. 漏斗收斂：強制行動呼籲 (CTA)
# ==========================================
st.markdown("---")
st.markdown("### 🛑 拒絕資訊不對稱的剝削")
st.markdown("Naval Motors 的 $P_{max}$ 演算法，專為消滅上述隱藏成本而生。我們只尋找「前車主已買單耗材」或「市價錯殺空間大於 15%」的絕對防禦型資產。")

if st.button("🚀 支付 NT$ 3,000 啟動金，授權 Naval 幫我攔截資產", type="primary", use_container_width=True):
    st.success("（系統已記錄意向。正在為您串接綠界科技支付閘道與委任電子合約...）")
    st.balloons() # 給客戶一點視覺多巴胺

st.caption("Disclaimer: 本試算器依據 2026 年 Q1 市場回溯數據建構。二手車資產存在個體差異，真實 TCO 需經 Naval Motors 現場 OBD2 與物理查驗後方可鎖定。")
