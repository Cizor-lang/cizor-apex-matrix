import streamlit as st
import json
import ssl
import websocket
import pandas as pd
import threading
import time
from datetime import datetime

# --- DASHBOARD UI CONFIGURATION ---
st.set_page_config(page_title="CHITI Over/Under Bot", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .block-container {padding-top: 0.4rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
    h1, h2, h3 {margin-bottom: 0.1rem; margin-top: 0.1rem; font-size: 1.1rem !important;}
    div[data-testid="metric-container"] {background-color: #0d0d0d; padding: 0.15rem 0.4rem; border-radius: 4px; border: 1px solid #1a1a1a;}
    </style>
""", unsafe_allow_html=True)

# --- AUTHENTICATION ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if not st.session_state.authenticated:
    st.title("🔒 CIZOR APEX INTERCEPT GATEWAY")
    input_passkey = st.text_input("ENTER PASSKEY:", type="password")
    if st.button("🚀 RELEASE SNIPER ENGINE"):
        if input_passkey == "2PRK9HH#":
            st.session_state.authenticated = True
            st.rerun()
    st.stop()

# --- MARKET MAP ---
MARKETS = {"Volatility 10 (1s)": "1HZ10V", "Volatility 25 (1s)": "1HZ25V", "Volatility 50 (1s)": "1HZ50V", "Volatility 75 (1s)": "1HZ75V", "Volatility 100 (1s)": "1HZ100V"}

# --- PERSISTENT STATES ---
state_defaults = {"running": False, "tracked_balance": 0.00, "total_wins": 0, "total_losses": 0, "consecutive_losses": 0, "history": [], "live_quote": 0.00, "last_digit": 0, "digit_window": [], "cooldown_until": 0}
for key, val in state_defaults.items():
    if key not in st.session_state: st.session_state[key] = val

with st.sidebar:
    app_id = st.text_input("App ID", value="1089")
    token = st.text_input("API Token", type="password")
    selected_market_name = st.selectbox("Target", list(MARKETS.keys()))
    symbol = MARKETS[selected_market_name]
    min_stake = st.number_input("Min Stake", value=0.50)
    risk_percentage = st.slider("Risk (%)", 1.0, 20.0, 2.0)
    if st.button("▶️ START"): st.session_state.running = True; st.rerun()
    if st.button("🛑 STOP"): st.session_state.running = False; st.rerun()

# --- HUD ---
m1, m2, m3, m4 = st.columns(4)
balance_slot = m1.metric("Balance", f"${st.session_state.tracked_balance:.2f}")
wins_slot = m2.metric("Wins", st.session_state.total_wins)
losses_slot = m3.metric("Losses", st.session_state.total_losses)
strategy_log_slot = st.empty()
ledger_slot = st.empty()

def fire_synchronized_contract(url, token, base_stake, target_type, target_pred, symbol):
    try:
        ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        ws.connect(url)
        ws.send(json.dumps({"authorize": token}))
        ws.recv()
        order = {"buy": 1, "price": float(base_stake), "parameters": {"amount": float(base_stake), "basis": "stake", "contract_type": target_type, "currency": "USD", "duration": 1, "duration_unit": "t", "barrier": str(target_pred), "symbol": symbol}}
        ws.send(json.dumps(order))
        buy_res = json.loads(ws.recv())
        if "buy" in buy_res:
            st.session_state.history.insert(0, {"Outcome": "PENDING", "Strategy": f"{target_type} {target_pred}"})
        ws.close()
    except: pass

# --- MAIN LOOP ---
if st.session_state.running:
    url = f"wss://ws.derivws.com/websockets/v3?app_id={app_id}"
    ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    ws.connect(url)
    ws.send(json.dumps({"authorize": token}))
    ws.send(json.dumps({"ticks": symbol, "balance": 1, "subscribe": 1}))
    
    while st.session_state.running:
        data = json.loads(ws.recv())
        if "balance" in data:
            new_bal = float(data["balance"]["balance"])
            if new_bal > st.session_state.tracked_balance:
                st.session_state.total_wins += 1; st.session_state.consecutive_losses = 0
            elif new_bal < st.session_state.tracked_balance:
                st.session_state.total_losses += 1; st.session_state.consecutive_losses += 1
            st.session_state.tracked_balance = new_bal
            wins_slot.metric("Wins", st.session_state.total_wins)
            losses_slot.metric("Losses", st.session_state.total_losses)
            if st.session_state.consecutive_losses >= 3: st.session_state.cooldown_until = time.time() + 10
        
        if "tick" in data:
            digit = int(str(data["tick"]["quote"])[-1])
            st.session_state.digit_window.append(digit)
            if len(st.session_state.digit_window) > 10: st.session_state.digit_window.pop(0)
            
            if time.time() < st.session_state.cooldown_until: continue
            
            recent = st.session_state.digit_window[-3:]
            target_type, target_pred = None, None
            
            # Optimized Logic
            if all(d <= 2 for d in recent): # Trend toward Low
                target_type, target_pred = "DIGITUNDER", 8
            elif all(d >= 7 for d in recent): # Trend toward High
                target_type, target_pred = "DIGITOVER", 2
                
            if target_type:
                stake = max(min_stake, st.session_state.tracked_balance * (risk_percentage / 100))
                threading.Thread(target=fire_synchronized_contract, args=(url, token, stake, target_type, target_pred, symbol), daemon=True).start()
                time.sleep(2)