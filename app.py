import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 页面设置
st.set_page_config(page_title="TQQQ 年线(MA250)交易指挥部", layout="wide")

st.title("📊 TQQQ 趋势定投实时信号灯 (MA250 准则)")
st.write("策略逻辑：IXIC 站上 MA250 则全线进攻；跌破 MA250 则立即清仓。")

# 1. 抓取最新数据
@st.cache_data(ttl=3600) # 每小时自动刷新一次
def get_data():
    # 获取纳指 IXIC 数据
    df = yf.download("^IXIC", start="2021-01-01")
    if isinstance(df.columns, pd.MultiIndex): 
        df.columns = df.columns.get_level_values(0)
    # 计算 MA250
    df['MA250'] = df['Close'].rolling(window=250).mean()
    return df

try:
    data = get_data()
    curr_price = float(data['Close'].iloc[-1])
    ma250 = float(data['MA250'].iloc[-1])
    last_update = data.index[-1].date()

    # 2. 核心逻辑判断
    # 距离年线的百分比
    dist_from_ma250 = (curr_price / ma250 - 1) * 100

    if curr_price > ma250:
        status = "🐂 强势牛市"
        color = "green"
        action = "【 满仓持有 + 正常定投 】"
        sub_text = f"当前价格高于年线 {dist_from_ma250:.2f}%，趋势向上。"
    else:
        status = "🐻 弱势熊市"
        color = "red"
        action = "【 立即清仓 + 停止定投 】"
        sub_text = f"当前价格低于年线 {abs(dist_from_ma250):.2f}%，趋势向下。"

    # 3. 页面仪表盘展示
    col1, col2, col3 = st.columns(3)
    col1.metric("纳指 IXIC 当前价", f"{curr_price:.2f}")
    col2.metric("MA250 (生命线)", f"{ma250:.2f}")
    col3.metric("距年线距离", f"{dist_from_ma250:.2f}%")

    st.markdown(f"""
    ---
    ### 📅 数据更新至: {last_update}
    ### 当前市场环境: <span style='color:{color}; font-size:30px;'>{status}</span>
    ### 💡 今日操作建议: <span style='color:{color}; font-size:40px; font-weight:bold;'>{action}</span>
    **状态说明**: {sub_text}
    ---
    """, unsafe_allow_html=True)

    # 4. 实时图表
    st.subheader("最近两年走势与 MA250 年线图")
    # 只显示有均线的数据部分
    plot_df = data.tail(500).dropna(subset=['MA250'])
    st.line_chart(plot_df[['Close', 'MA250']])

except Exception as e:
    st.error(f"数据加载出错，请稍后再试。错误信息: {e}")

st.sidebar.markdown("""
### 📖 操作指南
1. **卖出 QQQ Put**: 每天继续卖出 -8% 的 Weekly Put 收取权利金。
2. **定投 TQQQ**: 每月 21 日，若信号为 **绿色**，将收到的权利金买入 TQQQ。
3. **强制清仓**: 一旦信号变 **红色**，无论亏盈，立即卖出所有 TQQQ。
""")
st.sidebar.info("建议每天收盘前查看一次信号。")
