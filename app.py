import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="TQQQ 趋势交易指挥部", layout="wide")

st.title("📊 TQQQ 趋势定投实时信号灯")
st.write("策略：IXIC 站上 MA250 入场/定投，跌破 MA200 清仓避险。")

# 1. 抓取最新数据
@st.cache_data(ttl=3600) # 每小时更新一次数据
def get_data():
    df = yf.download("^IXIC", start="2020-01-01")
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df['MA200'] = df['Close'].rolling(window=200).mean()
    df['MA250'] = df['Close'].rolling(window=250).mean()
    return df

data = get_data()
curr_price = data['Close'].iloc[-1]
ma200 = data['MA200'].iloc[-1]
ma250 = data['MA250'].iloc[-1]
last_update = data.index[-1].date()

# 2. 逻辑判断
status = ""
color = ""
action = ""

if curr_price > ma250:
    status = "🐂 牛市环境"
    color = "green"
    action = "【保持持仓 / 每月21日继续定投】"
elif curr_price < ma200:
    status = "🐻 熊市环境"
    color = "red"
    action = "【清仓信号 / 停止定投 / 现金收租】"
else:
    status = "⚖️ 震荡区间"
    color = "orange"
    action = "【观望 / 维持上一动作状态】"

# 3. 页面展示
col1, col2, col3 = st.columns(3)
col1.metric("纳指 IXIC 当前价", f"{curr_price:.2f}")
col2.metric("MA200 (卖出线)", f"{ma200:.2f}")
col3.metric("MA250 (买入线)", f"{ma250:.2f}")

st.markdown(f"""
---
### 📅 数据日期: {last_update}
### 当前状态: <span style='color:{color}; font-size:30px;'>{status}</span>
### 今日操作建议: <span style='color:{color}; font-size:40px; font-weight:bold;'>{action}</span>
---
""", unsafe_allow_html=True)

# 4. 实时图表
st.subheader("最近一年均线趋势图")
plot_df = data.tail(250)
st.line_chart(plot_df[['Close', 'MA200', 'MA250']])

st.write("注：本系统仅供策略参考，不构成投资建议。")
