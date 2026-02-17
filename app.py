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

# --- 2. 數據讀取與強力清洗 ---
@st.cache_data
def load_and_clean_data():
    try:
        # 讀取 CSV
        df = pd.read_csv('clean_toyota_data.csv')
        
        # 1. 先把欄位名稱改對 (配合你的 CSV)
        df = df.rename(columns={
            'Model': 'series',
            'Year': 'year',
            'Price': 'price',
            'Raw_Text': 'desc'
        })

        # 2. 【關鍵修復】踢掉壞掉的資料
        # 如果 year 或 price 是空的 (NaN)，直接丟掉該行
        df = df.dropna(subset=['year', 'price'])

        # 3. 年份格式清洗
        # 把 "2012/03" 切開只拿 "2012"
        # 先轉成字串 -> 切割 -> 拿第一段 -> 轉數字
        df['year'] = df['year'].astype(str).str.split('/').str[0]
        
        # 過濾掉非數字的年份 (再次確保安全)
        df = df[df['year'].str.isnumeric()]
        df['year'] = df['year'].astype(int)

        # 4. 價格清洗
        # 確保價格是數字
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df = df.dropna(subset=['price']) # 再次踢掉轉失敗的價格

        return df
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"數據清洗失敗: {e}")
        return None

df = load_and_clean_data()

if df is None:
    st.error("❌ 找不到 clean_toyota_data.csv，請確認檔案是否已上傳。")
    st.stop()

# --- 3. 側邊欄 (Sidebar) ---
st.sidebar.header("🔍 查詢您的目標車輛")

# 選擇車型
# 如果資料庫只有 LEXUS，這裡只會顯示 LEXUS (因為你的 CSV Model 欄位似乎沒有細分型號)
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
    st.warning(f"⚠️ 數據不足：{selected_year} 年的 {selected_model} 只有 {len(target_cars)} 筆資料。")
    st.write("以下是原始資料供參考：")
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
        # 注意：這裡顯示的是資料庫裡的價格
        st.metric("資料庫行情 (中位數)", f"{market_median/10000:.1f} 萬")
    with col3:
        if price_diff > 0:
            st.metric("價差 (您高於行情)", f"{price_diff/10000:.1f} 萬", delta=f"-{price_diff/10000:.1f} 萬", delta_color="inverse")
        else:
            st.metric("價差 (您低於行情)", f"{abs(price_diff)/10000:.1f} 萬", delta=f"+{abs(price_diff)/10000:.1f} 萬")

    st.markdown("---")

    # --- 6. 視覺化圖表 ---
    st.subheader("📉 價格分佈圖")
    
    try:
        # 準備繪圖數據
        hist_data = [target_cars['price']]
        group_labels = ['市場行情']

        # 建立圖表 
        # bin_size 設為 20000 
        fig = ff.create_distplot(hist_data, group_labels, bin_size=20000, show_hist=True, show_rug=False)

        # 加入用戶開價的紅線
        fig.add_vline(
            x=user_price_raw, 
            line_width=3, 
            line_dash="dash", 
            line_color="red",
            annotation_text="您的位置", 
            annotation_position="top right"
        )

        fig.update_layout(
            title_text='',
            xaxis_title='價格 (元)',
            yaxis_title='分佈密度',
            showlegend=False,
            height=450,
            margin=dict(l=20, r=20, t=30, b=20),
        )
        fig.update_yaxes(showticklabels=False, showgrid=False)

        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"圖表繪製失敗: {e}")

    # --- 7. 資料洞察警告 (針對拍場起標價的問題) ---
    if market_median < 200000:
        st.warning(f"⚠️ 注意：資料庫中的行情 ({market_median/10000:.1f}萬) 似乎偏低。")
        st.info("💡 這可能代表您的資料來源是『拍賣場起標價』而非『市場成交價』。建議將此系統定位為「成本分析」而非「市價比對」。")

st.markdown("---")
st.caption("Naval Motors Intelligence System")
