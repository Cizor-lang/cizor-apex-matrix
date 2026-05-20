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

# (Keep your CSS styling exactly as it was)
st.markdown("""
    <style>
    .block-container {padding-top: 0.4rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
    h1, h2, h3 {margin-bottom: 0.1rem; margin-top: 0.1rem; font-size: 1.1rem !important;}
    div[data-testid="metric-container"] {background-color: #0d0d0d; padding: 0.15rem 0.4rem; border-radius: 4px; border: 1px solid #1a1a1a;}
    div[data-testid="stCodeBlock"] {margin-bottom: 0.1rem;}
    </style>
""", unsafe_allow_html=True)

# --- PERSISTENT MEMORY STATES ---
state_defaults = {
    "running": False,
    "tracked_balance": 0.00,
    "total_wins": 0,
    "total_losses": 0,
    "consecutive_losses": 0,
    "history": [],
    "current_action": "ENGINE INITIALIZED",
    "live_quote": 0.00,
    "last_digit": 0,
    "digit_window": [],
    "cooldown_until": 0,
    "last_trade_time": 0, # NEW: Prevents double counting
    "current_stake": 0.50 # NEW: Tracks live stake
}

for key, val in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- SIDEBAR & AUTH ---
# (Keeping your Auth and Sidebar logic identical)
# ... [Insert your Auth & Sidebar logic here] ...

# --- MAIN LOOP RUNNER ---
if st.session_state.running:
    # ... [Initialize WebSocket and Auth] ...
    
    while st.session_state.running:
        res = ws.recv()
        data = json.loads(res)
        
        # Calculate dynamic stake for display
        st.session_state.current_stake = max(min_stake, round(st.session_state.tracked_balance * (risk_percentage / 100.0), 2))
        
        if "balance" in data:
            new_bal = float(data["balance"]["balance"])
            diff = new_bal - prev_balance
            
            # THE FIX: Only process if significant difference and 3 seconds passed since last trade
            if abs(diff) > 0.001 and (time.time() - st.session_state.last_trade_time) > 3:
                st.session_state.last_trade_time = time.time() # Lock trade time
                
                if diff > 0:
                    st.session_state.total_wins += 1
                    # ... [Update Win UI] ...
                else:
                    st.session_state.total_losses += 1
                    # ... [Update Loss UI] ...
                
                st.session_state.tracked_balance = new_bal
                prev_balance = new_bal
                st.rerun() # Refresh UI
            continue

        if "tick" in data:
            # ... [Keep your Digit Window and Strategy Logic here] ...
            
            # When firing trade:
            if target_type is not None:
                st.session_state.current_stake = base_stake 
                # ... [Fire trade thread] ...