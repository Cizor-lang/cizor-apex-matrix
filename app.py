import streamlit as st
import asyncio
import websockets
import json
import pandas as pd
from datetime import datetime

# --- CONFIGURATION & SESSION STATE ---
st.set_page_config(page_title="CHITI Over/Under Bot", page_layout="wide")
st.title("🧬 CHITI Engine - Digit Over/Under")

if "running" not in st.session_state:
    st.session_state.running = False
if "history" not in st.session_state:
    st.session_state.history = []

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Core Parameters")
    app_id = st.text_input("App ID", value="1089") # Default demo app_id
    token = st.text_input("API Token", type="password")
    
    symbol = st.selectbox("Asset Index", ["R_10", "R_25", "R_50", "R_75", "R_100"])
    trade_type = st.radio("Trade Condition", ["DIGITUNDER", "DIGITOVER"])
    prediction = st.slider("Digit Prediction Target", 0, 9, 5)
    
    stake = st.number_input("Stake ($)", min_value=0.35, value=1.0, step=0.5)
    duration = st.integer_input("Duration (Ticks)", min_value=1, max_value=1, value=1) # O/U standard is 1 tick

    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ START BOT", use_container_width=True):
            if token:
                st.session_state.running = True
            else:
                st.error("Missing Token!")
    with col2:
        if st.button("🛑 STOP BOT", use_container_width=True):
            st.session_state.running = False

# --- LIVE METRICS INTERFACE ---
m1, m2, m3, m4 = st.columns(4)
tick_placeholder = m1.empty()
last_digit_placeholder = m2.empty()
profit_placeholder = m3.empty()
status_placeholder = m4.empty()

table_placeholder = st.empty()

# --- CORE TRADING CORE ENGINE ---
async def trade_loop():
    url = f"wss://ws.derivws.com/websockets/v3?app_id={app_id}"
    
    async with websockets.connect(url) as ws:
        # 1. Authenticate immediately
        auth_req = {"authorize": token}
        await ws.send(json.dumps(auth_req))
        auth_res = await ws.recv()
        auth_data = json.loads(auth_res)
        
        if "error" in auth_data:
            st.error(f"Auth Failed: {auth_data['error']['message']}")
            st.session_state.running = False
            return
            
        status_placeholder.metric("Engine Status", "Connected & Authorized")

        # 2. Subscribe to streaming ticks
        tick_req = {"ticks": symbol}
        await ws.send(json.dumps(tick_req))
        
        # Balance tracker for profit calculation
        initial_balance = float(auth_data["authorize"]["balance"])
        
        while st.session_state.running:
            try:
                res = await ws.recv()
                data = json.loads(res)
                
                if "tick" in data:
                    tick_val = data["tick"]["quote"]
                    tick_str = str(tick_val)
                    last_digit = int(tick_str[-1])
                    
                    tick_placeholder.metric("Live Quote", tick_val)
                    last_digit_placeholder.metric("Last Digit", last_digit)
                    
                    # 3. Simple execution rules logic
                    should_buy = False
                    if trade_type == "DIGITOVER" and last_digit > prediction:
                        should_buy = True
                    elif trade_type == "DIGITUNDER" and last_digit < prediction:
                        should_buy = True
                        
                    if should_buy:
                        contract_req = {
                            "buy": 1,
                            "price": stake,
                            "parameters": {
                                "amount": stake,
                                "basis": "stake",
                                "contract_type": trade_type,
                                "currency": "USD",
                                "duration": duration,
                                "duration_unit": "t",
                                "prediction": prediction,
                                "symbol": symbol
                            }
                        }
                        await ws.send(json.dumps(contract_req))
                        
                elif "buy" in data:
                    # Capture contract purchase details safely
                    p_id = data["buy"]["contract_id"]
                    st.session_state.history.insert(0, {
                        "Timestamp": datetime.now().strftime("%H:%M:%S"),
                        "Contract ID": p_id,
                        "Action": "Order Placed",
                        "Stake": stake
                    })
                    
                elif "proposal_open_contract" in data:
                    # Captures closures to dynamically update metrics
                    poc = data["proposal_open_contract"]
                    if poc.get("is_expired"):
                        profit = float(poc.get("profit", 0))
                        # Quick update to dashboard history logs
                        if st.session_state.history:
                            st.session_state.history[0]["Result"] = "WIN" if profit > 0 else "LOSS"
                            st.session_state.history[0]["Profit/Loss"] = profit

                # Keep interface clean and update layout frame
                if st.session_state.history:
                    df = pd.DataFrame(st.session_state.history).head(15)
                    table_placeholder.dataframe(df, use_container_width=True)
                    
            except Exception as e:
                st.sidebar.error(f"Loop Exception: {str(e)}")
                break

# --- STREAMLIT SYNC TO ASYNC RUNNER ---
if st.session_state.running:
    asyncio.run(trade_loop())
else:
    status_placeholder.metric("Engine Status", "Offline")