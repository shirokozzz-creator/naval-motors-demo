import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import numpy as np

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="Naval Motors 估價神器 (Pro)",
    page_icon="🚘",
    layout="wide"
)

# --- 2. 數據讀取與強力清洗 ---
@st.cache_data
def load_and_clean_data():
    try:
        # 讀取 CSV
        df = pd.read_csv('clean_toyota_data.csv')
        
        # 1. 欄位名稱標準化 (不管 CSV 寫什麼，都轉成我們看的懂的)
        # 這裡會嘗試抓各種可能的寫法
        df.columns = df.columns.str.strip().str.lower() # 全部轉小寫
        
        rename_map = {
            'model': 'series',
            'series': 'series', # 防呆
            'year': 'year',
            'price': 'price',
            'naval_price': 'naval_price',
            'raw_text': 'desc'
        }
        df = df.rename(columns=rename_map)

        # 2. 確保關鍵欄位存在，不存在就創一個空的
        if 'series' not in df.columns:
            # 嘗試找看看有沒有叫 lexus 或 toyota 的欄位
            df['series'] = 'Unknown' 
        
        # 3. 年份清洗 (把 "2012/03" 變成 2012)
        df['year'] = df['year'].astype(str).str.split('/').str[0]
        df = df[df['year'].str.isnumeric()] # 只留數字
        df['year'] = df['year'].astype(int)

        # 4. 價格清洗 (轉成數字)
        # 優先使用 Naval_Price (如果有)，沒有則用 Price
        target_price_col = 'naval_price' if 'naval_price' in df.columns else 'price'
        
        df['price'] = pd.to_numeric(df[target_price_col], errors='coerce')
        df = df.dropna(subset=['price']) # 踢掉沒價格的
        
        return df
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"數據讀取發生錯誤: {e}")
        return None

df = load_and_clean_data()

if df is None:
    st.error("❌ 找不到 clean_toyota_data.csv，請確認檔案是否已上傳。")
    st.stop()

# --- 3. 側邊欄：控制中心 (Control Panel) ---
st.sidebar.title("⚙️ 參數設定")

# [新增] 匯率/倍率修正器
st.sidebar.subheader("💰 數據校正")
st.sidebar.info("如果行情顯示只有 5~6 萬，可能是單位問題 (美金/起標價)。試著調整倍率！")
price_multiplier = st.sidebar.number_input(
    "價格倍率修正 (乘數)", 
    value=1.0, 
    min_value=0.1, 
    max_value=100.0, 
    step=0.1,
    help="如果是美金請填 32，如果是低價起標請填 1.2~1.5"
)

# 應用倍率到數據
df['adjusted_price'] = df['price'] * price_multiplier

# [新增] 垃圾數據過濾
filter_threshold = st.sidebar.number_input("過濾低於此價格的異常車源 (萬)", value=10, step=5) * 10000
df_clean = df[df['adjusted_price'] > filter_threshold].copy() # 只留正常車

st.sidebar.markdown("---")

# 選擇車型
st.sidebar.subheader("🔍 搜尋條件")
model_list = sorted(df_clean['series'].unique())
selected_model = st.sidebar.selectbox("選擇車型", model_list)

# 選擇年份
year_list = sorted(df_clean[df_clean['series'] == selected_model]['year'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("選擇年份", year_list)

# 用戶開價
user_price_input = st.sidebar.number_input("網路上看到的開價 (萬)", min_value=1.0, value=50.0, step=1.0)
user_price_raw = user_price_input * 10000

# --- 4. 核心分析邏輯 ---
target_cars = df_clean[(df_clean['series'] == selected_model) & (df_clean['year'] == selected_year)]

# --- 5. 主畫面儀表板 ---
st.title(f"📊 {selected_year} {selected_model} 市場行情分析")

if len(target_cars) < 2:
    st.warning(f"⚠️ 數據不足：經校正與過濾後，{selected_year} 年的 {selected_model} 剩餘 {len(target_cars)} 筆有效資料。")
    st.write("原始資料預覽：")
    st.dataframe(df.head())
else:
    # 計算指標
    market_median = target_cars['adjusted_price'].median()
    market_min = target_cars['adjusted_price'].min()
    market_max = target_cars['adjusted_price'].max()
    price_diff = user_price_raw - market_median
    
    # 顯示三大 KPI
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("您的目標開價", f"{user_price_input} 萬")
    with col2:
        st.metric(f"大數據行情 (中位數)", f"{market_median/10000:.1f} 萬", help="已應用倍率修正")
    with col3:
        if price_diff > 0:
            st.metric("潛在溢價", f"{price_diff/10000:.1f} 萬", delta=f"-{price_diff/10000:.1f} 萬 (買貴)", delta_color="inverse")
        else:
            st.metric("潛在價差", f"{abs(price_diff)/10000:.1f} 萬", delta=f"+{abs(price_diff)/10000:.1f} 萬 (划算)")

    # --- 6. 互動式圖表 ---
    st.subheader("📉 價格分佈光譜")
    
    try:
        # 使用 Histogram 取代 Distplot，更穩定且不易報錯
        import plotly.express as px
        
        fig = px.histogram(
            target_cars, 
            x="adjusted_price",
            nbins=20,
            title="市場價格分佈 (越高代表車源越多)",
            labels={"adjusted_price": "價格 (元)"},
            opacity=0.7,
            color_discrete_sequence=['#00CC96'] # 使用 Naval 綠
        )

        # 加入用戶紅線
        fig.add_vline(x=user_price_raw, line_width=3, line_dash="dash", line_color="red")
        fig.add_annotation(x=user_price_raw, y=0, text="您的位置", showarrow=True, arrowhead=1)

        # 優化 X 軸顯示 (以萬為單位)
        fig.update_layout(
            xaxis_title="預估成交價",
            yaxis_title="車輛數",
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"圖表繪製錯誤: {e}")

    # --- 7. 決策建議 ---
    st.markdown("### 📝 Naval 決策建議")
    if price_diff > 50000:
        st.error(f"🚫 **Low EV (低期望值)**：此價格高於行情 {price_diff/10000:.1f} 萬。建議直接放棄，或使用我們的『通病檢查表』進行殺價。")
    elif price_diff < -30000:
        st.success(f"✅ **High EV (高期望值)**：此價格低於行情，若車況正常 (無重大事故)，這是一個極佳的套利機會。")
    else:
        st.info(f"⚖️ **Fair Value (合理價格)**：價格符合市場預期。重點應轉向檢查車況細節。")

    with st.expander("查看詳細車源數據 (已過濾)"):
        st.dataframe(target_cars[['series', 'year', 'desc', 'adjusted_price']].sort_values('adjusted_price'))

st.markdown("---")
st.caption("Powered by Naval Motors | Data Calibrated by User")
