import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import numpy as np

# --- 1. 系統設定 ---
st.set_page_config(page_title="Naval Motors", page_icon="🏎️", layout="wide")

# --- 2. 數據核心 (含自動校正引擎) ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('clean_toyota_data.csv')
        
        # 欄位正規化：不管 CSV 標題是大寫小寫，通通轉成統一格式
        df.columns = df.columns.str.strip().str.lower() 
        rename_map = {
            'model': 'series',
            'year': 'year',
            'price': 'price',
            'naval_price': 'price', # 如果有 Naval 預測價，優先使用
            'raw_text': 'desc'
        }
        df = df.rename(columns=rename_map)

        # 確保關鍵欄位存在
        if 'series' not in df.columns: df['series'] = 'Unknown'
        
        # 年份清洗：把 "2012/03" 變成 2012
        df['year'] = df['year'].astype(str).str.split('/').str[0]
        df = df[df['year'].str.isnumeric()]
        df['year'] = df['year'].astype(int)

        # 價格清洗
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df = df.dropna(subset=['price'])
        
        # 🚨【關鍵修正】自動校正數量級
        # 如果全場中位數低於 20 萬，極有可能是數據少了一個 0
        if df['price'].median() < 200000:
            df['price'] = df['price'] * 10
            
        return df
    except Exception as e:
        return None

df = load_data()

# --- 3. 介面層 ---
if df is None:
    st.error("❌ 系統錯誤：找不到 clean_toyota_data.csv，請確認檔案已上傳。")
    st.stop()

# 側邊欄
st.sidebar.header("🔍 估價參數")
model_list = sorted(df['series'].unique())
selected_model = st.sidebar.selectbox("車型", model_list)
year_list = sorted(df[df['series'] == selected_model]['year'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("年份", year_list)
user_price_input = st.sidebar.number_input("您的目標開價 (萬)", value=50.0, step=1.0)
user_price = user_price_input * 10000

# 核心篩選
target_cars = df[(df['series'] == selected_model) & (df['year'] == selected_year)]

# --- 4. 結果呈現 (還原經典版) ---
st.title(f"{selected_year} {selected_model} 市場行情")

if len(target_cars) >= 2:
    # 計算數據
    market_median = target_cars['price'].median()
    diff = user_price - market_median
    
    # 三大指標
    c1, c2, c3 = st.columns(3)
    c1.metric("您的開價", f"{user_price_input} 萬")
    c2.metric("大數據行情 (中位數)", f"{market_median/10000:.1f} 萬")
    
    # 價差邏輯
    if diff > 0:
        c3.metric("價差 (高於行情)", f"{diff/10000:.1f} 萬", delta=f"-{diff/10000:.1f} 萬", delta_color="inverse")
    else:
        c3.metric("價差 (低於行情)", f"{abs(diff)/10000:.1f} 萬", delta=f"+{abs(diff)/10000:.1f} 萬")

    st.markdown("---")

    # 圖表區 (Distplot 回歸)
    st.subheader("📉 車商成本分佈圖")
    
    try:
        # 建立圖表 (隱藏 rug 以保持乾淨)
        fig = ff.create_distplot(
            [target_cars['price']], 
            ['市場行情'], 
            bin_size=20000, 
            show_hist=True, 
            show_rug=False,
            colors=['#00CC96'] # Naval Green
        )

        # 標示用戶位置
        fig.add_vline(x=user_price, line_width=3, line_dash="dash", line_color="#FF4136")
        fig.add_annotation(x=user_price, y=0, text="您的位置", showarrow=True, arrowhead=1, yshift=10)

        # 極簡化圖表設定
        fig.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis_title="價格 (元)",
            yaxis_title="分佈密度",
            plot_bgcolor="rgba(0,0,0,0)" # 透明背景
        )
        # 隱藏 Y 軸那些看不懂的數字
        fig.update_yaxes(showticklabels=False, showgrid=False)
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.warning("數據過於集中，改用簡易圖表顯示。")
        st.bar_chart(target_cars['price'])

else:
    st.warning("⚠️ 該年份車源不足，無法進行統計分析。")
    st.dataframe(target_cars)

st.markdown("---")
st.caption("Naval Motors Intelligence")
