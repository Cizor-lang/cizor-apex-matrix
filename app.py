import streamlit as st
import json
import ssl
import websocket
import pandas as pd
import threading
import time
from datetime import datetime

# --- UI CONFIGURATION ---
st.set_page_config(page_title="CHITI Over/Under Bot", page_icon="⚡", layout="wide")
st.markdown("""<style>.block-container {padding-top: 0.4rem;} div[data-testid="metric-container"] {background-color: #0d0d0d;}</style>""", unsafe_allow_html=True)

# --- AUTHENTICATION ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if not st.session_state.authenticated:
    st.title("🔒 CIZOR APEX GATEWAY")
    if st.text_input("Passkey:", type="password") == "2PRK9HH#":
        if st.button("🚀 RELEASE"): st.session_state.authenticated = True; st.rerun()
    st.stop()

# --- PERSISTENT STATE ---
defaults = {
    "running": False, "tracked_balance": 0.00, "total_wins": 0, "total_losses": 0,
    "history": [], "current_action": "STANDBY", "last_digit": 0, "digit_window": [],
    "cooldown_until": 0, "last_trade_time": 0, "current_stake": 0.50
}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# --- SIDEBAR ---
with st.sidebar:
    app_id = st.text_input("App ID", "1089")
    token = st.text_input("API Token", type="password")
    risk = st.slider("Risk (%)", 1.0, 20.0, 2.0)
    min_stake = st.number_input("Min Stake ($)", 0.35, value=0.50)
    if st.button("▶️ START"): st.session_state.running = True; st.rerun()
    if st.button("🛑 STOP"): st.session_state.running = False; st.rerun()

# --- HUD ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Balance", f"${st.session_state.tracked_balance:.2f}")
m2.metric("Active Stake", f"${st.session_state.current_stake:.2f}")
m3.metric("Wins", st.session_state.total_wins)
m4.metric("Losses", st.session_state.total_losses)

# --- ENGINE ---
def fire_trade(url, token, stake, t_type, barrier, symbol):
    try:
        ws = websocket.create_connection(url, sslopt={"cert_reqs": ssl.CERT_NONE})
        ws.send(json.dumps({"authorize": token}))
        ws.send(json.dumps({"buy": 1, "price": stake, "parameters": {"amount": stake, "basis": "stake", "contract_type": t_type, "currency": "USD", "duration": 1, "duration_unit": "t", "barrier": str(barrier), "symbol": symbol}}))
        ws.close()
    except: pass

if st.session_state.running and "worker" not in st.session_state:
    def worker():
        url = f"wss://ws.derivws.com/websockets/v3?app_id={app_id}"
        ws = websocket.create_connection(url, sslopt={"cert_reqs": ssl.CERT_NONE})
        ws.send(json.dumps({"authorize": token}))
        ws.send(json.dumps({"ticks": "1HZ10V", "balance": 1, "subscribe": 1}))
        prev_bal = 0
        while st.session_state.running:
            data = json.loads(ws.recv())
            # UPDATE BALANCE & STATS (TIME-LOCKED)
            if "balance" in data:
                new_bal = data["balance"]["balance"]
                if prev_bal != 0 and abs(new_bal - prev_bal) > 0.01 and (time.time() - st.session_state.last_trade_time) > 4:
                    if new_bal > prev_bal: st.session_state.total_wins += 1
                    else: st.session_state.total_losses += 1
                    st.session_state.last_trade_time = time.time()
                prev_bal = new_bal
                st.session_state.tracked_balance = new_bal
                st.session_state.current_stake = max(min_stake, round(new_bal * (risk/100), 2))
            # STRATEGY
            if "tick" in data:
                digit = int(str(data["tick"]["quote"])[-1])
                st.session_state.digit_window.append(digit)
                if len(st.session_state.digit_window) > 4: st.session_state.digit_window.pop(0)
                # EXECUTION
                if len(st.session_state.digit_window) == 4 and (time.time() - st.session_state.last_trade_time) > 4:
                    ticks = st.session_state.digit_window
                    if ticks[-1] in [0,1] and ticks[-2] in [0,1,2]: # UNDER 8
                        threading.Thread(target=fire_trade, args=(url, token, st.session_state.current_stake, "DIGITUNDER", 8, "1HZ10V")).start()
                        st.session_state.last_trade_time = time.time()
                    elif ticks[-1] in [8,9] and ticks[-2] in [7,8,9]: # OVER 2
                        threading.Thread(target=fire_trade, args=(url, token, st.session_state.current_stake, "DIGITOVER", 2, "1HZ10V")).start()
                        st.session_state.last_trade_time = time.time()
        ws.close()
    st.session_state.worker = True
    threading.Thread(target=worker, daemon=True).start()

if st.session_state.running:
    time.sleep(0.5)
    st.rerun()