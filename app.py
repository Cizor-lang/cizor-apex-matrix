import streamlit as st
import json
import ssl
import websocket
import pandas as pd
import time
from datetime import datetime

# --- DASHBOARD UI CONFIGURATION ---
st.set_page_config(page_title="CHITI Sniper Engine", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .block-container {padding-top: 0.4rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
    h1, h2, h3 {margin-bottom: 0.1rem; margin-top: 0.1rem; font-size: 1.1rem !important;}
    div[data-testid="metric-container"] {background-color: #0d0d0d; padding: 0.15rem 0.4rem; border-radius: 4px; border: 1px solid #1a1a1a;}
    </style>
""", unsafe_allow_html=True)

# --- STATE INITIALIZATION ---
state_defaults = {
    "authenticated": False, "running": False, "tracked_balance": 0.00,
    "total_wins": 0, "total_losses": 0, "history": [],
    "live_quote": 0.00, "last_digit": 0, "digit_window": [],
    "last_trade_time": 0, "current_stake": 0.00 
}
for key, val in state_defaults.items():
    if key not in st.session_state: st.session_state[key] = val

# --- AUTHENTICATION ---
if not st.session_state.authenticated:
    st.title("🔒 CIZOR APEX INTERCEPT GATEWAY")
    if st.text_input("PASSKEY:", type="password") == "2PRK9HH#":
        if st.button("🚀 RELEASE ENGINE"):
            st.session_state.authenticated = True
            st.rerun()
    st.stop()

# --- SIDEBAR & PARAMS ---
with st.sidebar:
    app_id = st.text_input("App ID", value="1089")
    token = st.text_input("API Token", type="password")
    symbol = "1HZ10V"
    min_stake = st.number_input("Min Stake", value=0.50)
    risk = st.slider("Risk (%)", 1.0, 20.0, 2.0)
    
    if st.button("▶️ START"): st.session_state.running = True; st.rerun()
    if st.button("🛑 STOP"): st.session_state.running = False; st.rerun()

# --- DASHBOARD HUD ---
st.markdown(f"### CHITI CORE MATRIX: {'🟩 RUNNING' if st.session_state.running else '🟥 PAUSED'}")
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Balance", f"${st.session_state.tracked_balance:,.2f}")
m2.metric("Active Stake", f"${st.session_state.current_stake:,.2f}")
m3.metric("Wins", st.session_state.total_wins)
m4.metric("Losses", st.session_state.total_losses)
m5.metric("Ticker", f"{st.session_state.live_quote:.2f} [{st.session_state.last_digit}]")
m6.metric("Total", st.session_state.total_wins + st.session_state.total_losses)

ledger_slot = st.empty()

# --- TRADING LOGIC ---
if st.session_state.running:
    try:
        ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        ws.connect(f"wss://ws.derivws.com/websockets/v3?app_id={app_id}")
        ws.send(json.dumps({"authorize": token}))
        ws.recv()
        ws.send(json.dumps({"ticks": symbol, "balance": 1, "subscribe": 1}))
        
        while st.session_state.running:
            data = json.loads(ws.recv())
            
            if "balance" in data:
                new_bal = float(data["balance"]["balance"])
                diff = new_bal - st.session_state.tracked_balance
                
                # TIME-LOCK: Only process if change > 0.001 and > 3s since last trade
                if abs(diff) > 0.001 and (time.time() - st.session_state.last_trade_time) > 3:
                    st.session_state.last_trade_time = time.time()
                    if diff > 0: st.session_state.total_wins += 1
                    else: st.session_state.total_losses += 1
                    st.session_state.tracked_balance = new_bal
                    st.rerun()
            
            if "tick" in data:
                quote = float(data["tick"]["quote"])
                st.session_state.live_quote = quote
                st.session_state.last_digit = int(f"{quote:.2f}"[-1])
                st.session_state.current_stake = max(min_stake, round(st.session_state.tracked_balance * (risk/100), 2))
                st.rerun()
                
    except Exception:
        st.session_state.running = False
        st.rerun()

if st.session_state.history:
    ledger_slot.dataframe(pd.DataFrame(st.session_state.history).head(10), use_container_width=True)