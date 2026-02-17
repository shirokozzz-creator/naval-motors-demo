import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import numpy as np

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="Naval Motors 估價神器",
    page_icon="🚗",
    layout="wide"
)

# --- 2. 數據讀取與清洗 (關鍵修復區) ---
@st.cache_data
def load_and_clean_data():
    try:
        # 讀取 CSV
        df = pd.read_csv('clean_toyota_data.csv')
        
        # --- 🔧 自動欄位對應 (Fixing Columns) ---
        # 這裡把你的欄位名稱 (Model, Year, Price) 對應到程式邏輯
        df = df.rename(columns={
            'Model': 'series',
            'Year': 'year',
            'Price': 'price',
            'Raw_Text': 'desc'  # 保留描述欄位備用
        })
        
        # --- 🔧 年份格式清洗 (Fixing Year) ---
        # 把 "2012/03" 這種格式切開，只留 "2012"，並轉成數字
        #astype(str) 確保它是字串，split('/') 切割，str[0] 取第一段
        df['year'] = df['year'].astype(str).str.split('/').str[0].astype(int)
        
        return df
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"數據處理發生未預期的錯誤: {e}")
        return None

df = load_and_clean_data()

if df is None:
    st.error("❌ 找不到 clean_toyota_data.csv，請確認檔案是否已上傳。")
    st.stop()

# --- 3. 側邊欄 (Sidebar) ---
st.sidebar.header("🔍 查詢您的目標車輛")

# 選擇車型 (使用清洗後的 series 欄位)
# 備註：如果你的 Model 欄位只有 "LEXUS" 而沒有 "CT200h"，這裡只會出現 "LEXUS"
model_list = sorted(df['series'].unique())
selected_model = st.sidebar.selectbox("選擇車型", model_list)

# 根據車型連動選擇年份
year_list = sorted(df[df['series'] == selected_model]['year'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("選擇年份", year_list)

# 輸入網路上看到的開價 (單位：萬)
user_price_input = st.sidebar.number_input("您在網路上看到的開價 (萬)", min_value=1.0, max_value=200.0, value=50.0, step=0.5)
user_price_raw = user_price_input * 10000  # 換算成元

# --- 4. 核心邏輯 ---
# 篩選數據
target_cars = df[(df['series'] == selected_model) & (df['year'] == selected_year)]

# --- 5. 主畫面顯示 ---
st.title(f"📊 {selected_year} {selected_model} 市場行情分析")

if len(target_cars) < 2:
    st.warning(f"⚠️ 數據樣本不足：資料庫中 {selected_year} 年的 {selected_model} 筆數過少，無法畫出分佈圖。")
    # 就算不能畫圖，也嘗試顯示表格讓使用者參考
    st.dataframe(target_cars)
else:
    # 計算市場行情
    market_avg = target_cars['price'].mean()
    market_median = target_cars['price'].median()
    price_diff = user_price_raw - market_median
    
    # 顯示三大指標
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("您的目標開價", f"{user_price_input} 萬")
    with col2:
        st.metric("大數據估算成本 (中位數)", f"{market_median/10000:.1f} 萬")
    with col3:
        if price_diff > 0:
            st.metric("潛在溢價", f"{price_diff/10000:.1f} 萬", delta=f"-{price_diff/10000:.1f} 萬", delta_color="inverse")
        else:
            st.metric("潛在價差 (划算)", f"{abs(price_diff)/10000:.1f} 萬", delta=f"+{abs(price_diff)/10000:.1f} 萬")

    st.markdown("---")

    # --- 6. 視覺化圖表 (優化版) ---
    st.subheader("📉 車商成本 vs 市場開價分佈圖")
    
    # 準備繪圖數據
    hist_data = [target_cars['price']]
    group_labels = ['市場行情分佈']

    # 建立圖表 
    # bin_size 設為 20000 (2萬元) 讓曲線平滑
    try:
        fig = ff.create_distplot(hist_data, group_labels, bin_size=20000, show_hist=True, show_rug=False)

        # 加入用戶開價的紅線
        fig.add_vline(
            x=user_price_raw, 
            line_width=3, 
            line_dash="dash", 
            line_color="red",
            annotation_text=f"您的位置", 
            annotation_position="top right"
        )

        # 優化排版
        fig.update_layout(
            title_text='',
            xaxis_title='價格 (元)',
            yaxis_title='市場分佈密度',
            showlegend=False,
            height=450,
            margin=dict(l=20, r=20, t=30, b=20),
        )
        fig.update_yaxes(showticklabels=False, showgrid=False)

        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"圖表繪製失敗 (可能是數據過於集中): {e}")

    # --- 7. 下一步行動 (CTA) ---
    if price_diff > 30000:
        st.error(f"🚨 警告：這個開價比行情貴了約 {price_diff/10000:.1f} 萬！")
        st.button("🔥 點此索取殺價劇本 (Line)", type="primary")
    elif price_diff < -20000:
        st.success("✅ 這是一個非常不錯的價格，建議確認車況後儘快下手！")
    else:
        st.info("ℹ️ 價格符合行情，屬於合理範圍。")

st.markdown("---")
st.caption("Powered by Naval Motors Data Lab")
