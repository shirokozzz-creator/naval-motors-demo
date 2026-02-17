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

# --- 2. 數據讀取 (加入快取機制，加速運作) ---
@st.cache_data
def load_data():
    # 讀取你的 2899 筆黃金數據
    # 假設你的 csv 檔名是 clean_toyota_data.csv
    # 欄位假設包含: 'series'(車型), 'year'(年份), 'price'(價格), 'mileage'(里程)
    df = pd.read_csv('clean_toyota_data.csv')
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("錯誤：找不到 clean_toyota_data.csv，請確認檔案是否已上傳到 GitHub 或本地資料夾。")
    st.stop()

# --- 3. 側邊欄 (Sidebar) ---
st.sidebar.header("🔍 查詢您的目標車輛")

# 選擇車型
model_list = sorted(df['series'].unique())
selected_model = st.sidebar.selectbox("選擇車型", model_list)

# 根據車型連動選擇年份
year_list = sorted(df[df['series'] == selected_model]['year'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("選擇年份", year_list)

# 輸入網路上看到的開價 (單位：萬)
user_price_input = st.sidebar.number_input("您在網路上看到的開價 (萬)", min_value=10.0, max_value=200.0, value=50.0, step=0.5)
user_price_raw = user_price_input * 10000  # 換算成元

# --- 4. 核心邏輯 ---
# 篩選數據
target_cars = df[(df['series'] == selected_model) & (df['year'] == selected_year)]

# --- 5. 主畫面顯示 ---
st.title(f"📊 {selected_year} {selected_model} 市場行情分析")

if len(target_cars) < 3:
    st.warning(f"⚠️ 數據樣本不足：資料庫中 {selected_year} 年的 {selected_model} 只有 {len(target_cars)} 台，分析可能不夠精準。")
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
            st.metric("潛在溢價 (被貴了)", f"{price_diff/10000:.1f} 萬", delta=f"-{price_diff/10000:.1f} 萬", delta_color="inverse")
        else:
            st.metric("潛在價差 (划算)", f"{abs(price_diff)/10000:.1f} 萬", delta=f"+{abs(price_diff)/10000:.1f} 萬")

    st.markdown("---")

    # --- 6. 視覺化圖表 (優化版) ---
    st.subheader("📉 車商成本 vs 市場開價分佈圖")
    
    # 準備繪圖數據
    hist_data = [target_cars['price']]
    group_labels = ['市場行情分佈']

    # 建立圖表 (使用 distplot 但隱藏過於數學的細節)
    # bin_size 設為 20000 (2萬元) 讓曲線平滑
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

    # 優化排版 (移除看不懂的 Y 軸)
    fig.update_layout(
        title_text='', # 標題已在上面用 st.subheader 顯示
        xaxis_title='價格 (元)',
        yaxis_title='市場分佈密度',
        showlegend=False,
        height=450,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(
            tickmode='linear',
            dtick=50000  # X軸每 5 萬顯示一個刻度
        )
    )
    # 隱藏 Y 軸刻度
    fig.update_yaxes(showticklabels=False, showgrid=False)

    st.plotly_chart(fig, use_container_width=True)

    # --- 7. 下一步行動 (CTA) ---
    if price_diff > 30000:
        st.error(f"🚨 警告：這個開價比行情貴了約 {price_diff/10000:.1f} 萬！")
        st.markdown("這筆錢您可以省下來做大保養或換輪胎。我們手上有這年份的 **通病檢查表** 與 **議價話術**。")
        st.button("🔥 點此索取殺價劇本 (Line)", type="primary")
    elif price_diff < -20000:
        st.success("✅ 這是一個非常不錯的價格，建議確認車況後儘快下手！")
    else:
        st.info("ℹ️ 價格符合行情，屬於合理範圍。")

# 頁面底部
st.markdown("---")
st.caption("Powered by Naval Motors Data Lab | 數據來源：2899 筆實時市場交易紀錄")
