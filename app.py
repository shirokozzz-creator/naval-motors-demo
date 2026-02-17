import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go

# --- 設定網頁標題與佈局 ---
st.set_page_config(page_title="Naval Motors 價格揭密", page_icon="🚗")

# --- 1. 讀取數據 (肌肉記憶) ---
@st.cache_data
def load_data():
    # 讀取你剛剛煉金出來的 CSV
    df = pd.read_csv("clean_toyota_data.csv")
    
    # 資料清洗：確保年份是數字
    df['Year'] = df['Year'].astype(str).str.extract(r'(\d{4})')
    df = df.dropna(subset=['Year', 'Price'])
    df['Year'] = df['Year'].astype(int)
    
    # 建立一個「顯示用」的車型欄位 (包含數量)
    model_counts = df['Model'].value_counts()
    df['Model_Display'] = df['Model'].apply(lambda x: f"{x} ({model_counts.get(x, 0)}筆)")
    
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ 找不到 clean_toyota_data.csv，請確認檔案是否在同一個資料夾！")
    st.stop()

# --- 2. 側邊欄：使用者輸入 ---
st.sidebar.header("🔍 查詢您的目標車輛")

# 選擇車型 (連動選單)
model_list = sorted(df['Model'].unique())
selected_model = st.sidebar.selectbox("選擇車型", model_list, index=model_list.index('PRIUS') if 'PRIUS' in model_list else 0)

# 選擇年份 (只顯示該車型有的年份)
available_years = sorted(df[df['Model'] == selected_model]['Year'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("選擇年份", available_years)

# 用戶輸入：目前看到的市場開價 (用來打臉用)
st.sidebar.markdown("---")
user_price_input = st.sidebar.number_input("您在網路上看到的開價 (萬)", min_value=10, max_value=500, value=50, step=1)
user_price = user_price_input * 10000 # 轉成元

# --- 3. 核心邏輯：計算批發行情 ---
# 篩選數據
target_data = df[(df['Model'] == selected_model) & (df['Year'] == selected_year)]

if len(target_data) < 3:
    st.warning(f"⚠️ {selected_year} 年的 {selected_model} 樣本數不足 ({len(target_data)}筆)，數據可能不準確。")
else:
    # 計算 Naval 批發底價 (批發成本 + 15% 管銷)
    # 這裡直接用你 CSV 裡的 Wholesale_Est 或是現場算
    wholesale_prices = target_data['Price'] * 1.15 
    
    avg_wholesale = wholesale_prices.mean()
    min_wholesale = wholesale_prices.min()
    max_wholesale = wholesale_prices.max()
    
    # 計算價差 (暴利空間)
    profit_gap = user_price - avg_wholesale
    is_ripoff = profit_gap > 30000 # 如果價差超過 3萬，視為盤子

    # --- 4. 主畫面：恐懼行銷 ---
    st.title(f"📊 {selected_year} {selected_model} 真實行情分析")
    
    # 顯示核心數據卡片
    col1, col2, col3 = st.columns(3)
    col1.metric("網路上開價", f"{user_price/10000:.1f} 萬")
    col2.metric("車商預估成本", f"{avg_wholesale/10000:.1f} 萬", delta_color="inverse")
    col3.metric("潛在價差 (暴利)", f"{profit_gap/10000:.1f} 萬", 
                delta=f"-{profit_gap/10000:.1f} 萬" if is_ripoff else "合理",
                delta_color="normal" if is_ripoff else "off")

    st.markdown("---")

    # --- 5. 視覺化：價格分佈圖 ---
    # 使用 Plotly 畫分佈圖
    fig = ff.create_distplot([wholesale_prices], ['車商進貨成本分佈'], bin_size=10000, show_rug=False, colors=['#00CC96'])
    
    # 加上一條紅線：使用者的開價
    fig.add_shape(type="line",
        x0=user_price, y0=0, x1=user_price, y1=0.00005, # Y軸高度可能需微調
        line=dict(color="Red", width=4, dash="dashdot")
    )
    
    # 加上標註
    fig.add_annotation(x=user_price, y=0.00004, text=f"您的開價: {user_price/10000}萬", showarrow=True, arrowhead=1)
    
    fig.update_layout(title_text='車商成本 vs 市場開價', xaxis_title='價格 (元)', showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # --- 6. 結論與導流 (Call to Action) ---
    if is_ripoff:
        st.error(f"🚨 **警告：您查詢的價格比合理行情貴了約 {int(profit_gap/10000)} 萬元！**")
        st.markdown(f"""
        這筆錢您可以省下來做大保養或換輪胎。
        我們手上有這年份 {selected_model} 的**通病檢查表**與**議價話術**。
        """)
        
        # 導流按鈕 (這就是你的私人生意入口)
        # 用 HTML 語法做一個漂亮的按鈕
        line_url = "https://line.me/ti/p/你的ID" # 請換成你的 LINE 連結
        st.markdown(f'''
            <a href="{line_url}" target="_blank">
                <button style="
                    background-color: #d32f2f; 
                    color: white; 
                    padding: 12px 24px; 
                    border: none; 
                    border-radius: 4px; 
                    font-size: 16px; 
                    font-weight: bold; 
                    cursor: pointer; 
                    width: 100%;">
                    🔥 點此索取 {int(profit_gap/10000)} 萬元的殺價劇本 (LINE)
                </button>
            </a>
            ''', unsafe_allow_html=True)
            
    else:
        st.success("✅ **恭喜：這個價格在合理範圍內。**")
        st.info("但在簽約前，您確認過電池健康度與變速箱狀況了嗎？")
        line_url = "https://line.me/ti/p/你的ID"
        st.markdown(f"[💬 預約 Naval 專家驗車服務]({line_url})")