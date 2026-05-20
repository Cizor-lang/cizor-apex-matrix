import streamlit as st
import json
import ssl
import websocket
import pandas as pd
import threading
import time
from datetime import datetime

# --- FIXED SYSTEM DASHBOARD DESIGN SKIN ---
st.set_page_config(page_title="CHITI Over/Under Bot", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .block-container {padding-top: 0.4rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
    h1, h2, h3 {margin-bottom: 0.1rem; margin-top: 0.1rem; font-size: 1.1rem !important;}
    div[data-testid="metric-container"] {background-color: #0d0d0d; padding: 0.15rem 0.4rem; border-radius: 4px; border: 1px solid #1a1a1a;}
    div[data-testid="stCodeBlock"] {margin-bottom: 0.1rem;}
    </style>
""", unsafe_allow_html=True)

# --- SECURITY INTERCEPT GATEWAY ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 CIZOR APEX INTERCEPT GATEWAY")
    st.markdown("---")
    input_passkey = st.text_input("ENTER ONE-TIME OPERATIONAL AUTHENTICATION PASSKEY:", type="password")
    if st.button("🚀 RELEASE SNIPER ENGINE"):
        if input_passkey == "2PRK9HH#":
            st.session_state.authenticated = True
            st.success("✅ ACCESS GRANTED.")
            st.rerun()
        else:
            st.error("❌ INVALID SYSTEM PASSKEY.")
    st.stop()

# --- MARKET REGISTER ---
MARKETS = {
    "Volatility 10 (1s)": "1HZ10V",
    "Volatility 25 (1s)": "1HZ25V",
    "Volatility 50 (1s)": "1HZ50V",
    "Volatility 75 (1s)": "1HZ75V",
    "Volatility 100 (1s)": "1HZ100V"
}

# --- STATE MEMORY ARRAY ARCHITECTURE ---
state_defaults = {
    "running": False,
    "tracked_balance": 0.00,
    "total_wins": 0,
    "total_losses": 0,
    "history": [],
    "current_action": "ENGINE CORE STANDBY — READY TO HUNT",
    "live_quote": 0.00,
    "last_digit": 0,
    "digit_window": []
}

for key, val in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

total_executions = st.session_state.total_wins + st.session_state.total_losses

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Core Parameters")
    st.markdown("**AUTHOR:** CIZOR THE BADDEST")
    st.markdown("---")
    app_id = st.text_input("App ID", value="1089")
    token = st.text_input("API Token", type="password")
    selected_market_name = st.selectbox("Active Stream Target", list(MARKETS.keys()))
    symbol = MARKETS[selected_market_name]
    
    st.markdown("---")
    st.markdown("**⚡ CAPITAL RISK PROFILE**")
    min_stake = st.number_input("Minimum Stake ($)", min_value=0.35, value=0.50, step=0.05)
    risk_percentage = st.slider("Dynamic Risk Sizing (%)", min_value=1.0, max_value=20.0, value=3.0, step=0.5)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ START BOT", use_container_width=True):
            if token:
                st.session_state.running = True
                st.session_state.digit_window = []
                st.rerun()
    with col2:
        if st.button("🛑 STOP BOT", use_container_width=True):
            st.session_state.running = False
            st.rerun()

if st.button("🧹 PURGE METRICS STORAGE", use_container_width=True):
    st.session_state.total_wins = 0
    st.session_state.total_losses = 0
    st.session_state.history.clear()
    st.rerun()

st.markdown(f"### CHITI SCALPER MATRIX: {'🟩 OPERATIONAL' if st.session_state.running else '🟥 PAUSED'}")

m1, m2, m3, m4, m5 = st.columns(5)
balance_slot = m1.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f} USD")
trades_slot = m2.metric("Total Executions", total_executions)
wins_slot = m3.metric("Won Contracts", f"🟩 {st.session_state.total_wins}")
losses_slot = m4.metric("Lost Contracts", f"🟥 {st.session_state.total_losses}")
ticker_slot = m5.metric("Live Ticker Feed", f"{st.session_state.live_quote:.2f} [{st.session_state.last_digit}]")

strategy_log_slot = st.empty()
layout_left, layout_right = st.columns([4, 5])
with layout_left:
    st.markdown("### 📊 Distribution Spectrum (Last 15 Ticks)")
    spectrum_slot = st.empty()
with layout_right:
    st.markdown("### 📜 Real-Time Ledger")
    ledger_slot = st.empty()

# --- BROKER PROPOSAL PIPELINE ---
def execute_broker_trade(url, token, base_stake, target_type, target_pred, symbol):
    try:
        dispatch_ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        dispatch_ws.connect(url)
        dispatch_ws.send(json.dumps({"authorize": token}))
        
        contract_string = "DIGITMATCH" if target_type == "DIGITOVER" else "DIGITUNDER"
        order = {
            "buy": 1, "price": base_stake,
            "parameters": {
                "amount": base_stake, "basis": "stake", "contract_type": contract_string,
                "currency": "USD", "duration": 1, "duration_unit": "t",
                "barrier": str(target_pred), "symbol": symbol
            }
        }
        dispatch_ws.send(json.dumps(order))
        buy_res = json.loads(dispatch_ws.recv())
        dispatch_ws.close()
        
        if "buy" in buy_res:
            st.session_state.history.insert(0, {
                "Timestamp": datetime.now().strftime("%H:%M:%S"),
                "Setup": f"{target_type} {target_pred}",
                "Outcome": "PROCESSING", "Net P/L": "$0.00"
            })
    except: pass

# --- ACTIVE SNIPER LOOP ---
if st.session_state.running:
    url = f"wss://ws.derivws.com/websockets/v3?app_id={app_id}"
    ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    try:
        ws.connect(url)
        ws.send(json.dumps({"authorize": token}))
        ws.send(json.dumps({"ticks": symbol}))
        ws.send(json.dumps({"balance": 1, "subscribe": 1}))
        
        while st.session_state.running:
            res = ws.recv()
            data = json.loads(res)
            
            if "balance" in data:
                st.session_state.tracked_balance = float(data["balance"]["balance"])
            
            if "tick" in data:
                quote = float(data["tick"]["quote"])
                digit = int(f"{quote:.2f}"[-1])
                st.session_state.last_digit = digit
                st.session_state.digit_window.append(digit)
                if len(st.session_state.digit_window) > 15: st.session_state.digit_window.pop(0)
                
                # --- OPTIMIZED STRATEGY ENGINE: ONLY OVER 2 / UNDER 8 ---
                target_type = None
                target_pred = None
                
                # Only trigger if the digit allows for the strict high-probability set
                if digit > 2: # Potential OVER 2 candidate
                    target_type, target_pred = "DIGITOVER", 2
                elif digit < 8: # Potential UNDER 8 candidate
                    target_type, target_pred = "DIGITUNDER", 8
                
                if target_type:
                    calc_stake = st.session_state.tracked_balance * (risk_percentage / 100.0)
                    base_stake = max(min_stake, round(calc_stake, 2))
                    threading.Thread(target=execute_broker_trade, args=(url, token, base_stake, target_type, target_pred, symbol), daemon=True).start()
                    time.sleep(2.0)
                    
    except: st.session_state.running = False