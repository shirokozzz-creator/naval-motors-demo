import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import numpy as np

st.set_page_config(layout="wide", page_title="Naval Motors")

# --- 1. 讀取數據 (保留原始邏輯，但加上欄位對應以免報錯) ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('clean_toyota_data.csv')
        
        # 簡單暴力的欄位對應 (針對你的 CSV 格式)
        # 如果你的 CSV 欄位是大寫，這裡把它轉成程式慣用的小寫
        df = df.rename(columns={
            'Model': 'series',
            'Year': 'year',
            'Price': 'price',
            'Raw_Text': 'desc'
        })
        
        # 簡單清洗年份 (處理 2012/03 這種格式)
        df['year'] = df['year'].astype(str).str.split('/').str[0]
        df = df[df['year'].str.isnumeric()]
        df['year'] = df['year'].astype(int)
        
        # 確保價格是數字
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df = df.dropna(subset=['price'])
        
        return df
    except Exception as e:
        return None

df = load_data()

if df is None:
    st.error("讀取失敗，請確認 CSV 檔案存在。")
    st.stop()

# --- 2. 側邊欄 ---
st.sidebar.header("🔍 參數設定")
model_list = sorted(df['series'].unique())
selected_model = st.sidebar.selectbox("車型", model_list)

year_list = sorted(df[df['series'] == selected_model]['year'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("年份", year_list)

user_price_input = st.sidebar.number_input("開價 (萬)", value=50.0, step=0.5)
user_price_raw = user_price_input * 10000

# --- 3. 核心計算 ---
target_cars = df[(df['series'] == selected_model) & (df['year'] == selected_year)]

st.title(f"{selected_year} {selected_model} 行情分析")

if len(target_cars) > 1:
    market_avg = target_cars['price'].mean()
    market_median = target_cars['price'].median()
    diff = user_price_raw - market_median

    c1, c2, c3 = st.columns(3)
    c1.metric("您的開價", f"{user_price_input} 萬")
    c2.metric("市場行情 (中位數)", f"{market_median/10000:.1f} 萬")
    c3.metric("價差", f"{diff/10000:.1f} 萬", delta_color="inverse")

    st.markdown("---")
    
    # --- 4. 圖表修復區 (只改這裡) ---
    st.subheader("市場價格分佈圖")

    # 使用 distplot (原本的圖)，但把參數調得更人性化
    # bin_size=20000: 每 2 萬塊一格，讓圖形比較滑順
    fig = ff.create_distplot(
        [target_cars['price']], 
        ['市場價格'], 
        bin_size=20000, 
        show_hist=True, 
        show_rug=False # 關閉底部毛邊，看起來比較乾淨
    )

    # 加入你的紅線
    fig.add_vline(x=user_price_raw, line_width=3, line_dash="dash", line_color="red")
    
    # [關鍵修改] 隱藏看不懂的 Y 軸數字 (50μ)
    fig.update_layout(
        title_text="",
        xaxis_title="價格 (元)",
        yaxis_title="車輛數量密度", # 改個中文名字
        showlegend=False,
        height=400,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    # 把 Y 軸的刻度與數字全部隱藏
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
    
    # 設定 X 軸格式 (不要顯示 500k，顯示完整數字或讓 Plotly 自動處理)
    fig.update_xaxes(showgrid=True)

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("數據不足，無法繪圖")
