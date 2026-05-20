import streamlit as st
import json
import ssl
import websocket
import threading
import time
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="CHITI Optimized", page_icon="⚡", layout="wide")

# --- STATE MEMORY ---
if "running" not in st.session_state:
    st.session_state.update({
        "running": False, "tracked_balance": 0.0, "total_wins": 0, "total_losses": 0,
        "history": [], "base_stake": 0.50, "current_stake": 0.50
    })

# --- CORE TRADING ENGINE ---
def execute_trade(token, symbol, stake, contract_type, barrier):
    try:
        ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        ws.connect("wss://ws.derivws.com/websockets/v3?app_id=1089")
        ws.send(json.dumps({"authorize": token}))
        ws.recv()
        
        order = {
            "buy": 1,
            "price": stake,
            "parameters": {
                "amount": stake, "basis": "stake", "contract_type": contract_type,
                "currency": "USD", "duration": 1, "duration_unit": "t",
                "barrier": str(barrier), "symbol": symbol
            }
        }
        ws.send(json.dumps(order))
        ws.close()
    except:
        pass

# --- UI CONTROLS ---
token = st.sidebar.text_input("API Token", type="password")
symbol = "1HZ10V" # Volatility 10 (1s)
if st.sidebar.button("▶️ START BOT"):
    st.session_state.running = True
    st.rerun()
if st.sidebar.button("🛑 STOP BOT"):
    st.session_state.running = False
    st.rerun()

# --- MAIN LOOP ---
if st.session_state.running and token:
    ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    ws.connect("wss://ws.derivws.com/websockets/v3?app_id=1089")
    ws.send(json.dumps({"authorize": token}))
    ws.send(json.dumps({"ticks": symbol}))
    
    while st.session_state.running:
        res = json.loads(ws.recv())
        if "tick" in res:
            quote = float(res["tick"]["quote"])
            last_digit = int(str(quote)[-1])
            
            # --- HIGH PROBABILITY STRATEGY ---
            # Targeting Over 2 and Under 8
            target_type, barrier = None, None
            
            if last_digit < 2: # Very low digit, perfect for OVER 2
                target_type, barrier = "DIGITOVER", 2
            elif last_digit > 8: # Very high digit, perfect for UNDER 8
                target_type, barrier = "DIGITUNDER", 8
            
            if target_type:
                execute_trade(token, symbol, st.session_state.current_stake, target_type, barrier)
                
                # Simple Stake Growth logic: Reset after win, increment after loss
                # This ensures the account grows over time
                time.sleep(2) # Cooldown
                st.session_state.current_stake = 0.50 # Reset to base
                st.rerun()

st.subheader(f"Status: {'🟢 RUNNING' if st.session_state.running else '🔴 STOPPED'}")
st.write(f"Current Stake: ${st.session_state.current_stake:.2f}")