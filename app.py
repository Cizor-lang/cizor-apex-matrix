import streamlit as st
import asyncio
import websockets
import json
import pandas as pd
from datetime import datetime

# --- SYSTEM HEADER CONFIGURATION (CORRECTED PARAMETER) ---
st.set_page_config(page_title="CHITI Over/Under Bot", page_icon="⚡", layout="wide")

# --- INITIAL SECURITY GATEWAY ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 CIZOR APEX INTERCEPT GATEWAY")
    st.markdown("---")
    
    input_passkey = st.text_input("ENTER ONE-TIME OPERATIONAL AUTHENTICATION PASSKEY:", type="password")
    release_btn = st.button("🚀 RELEASE SNIPER ENGINE")
    
    if release_btn:
        if input_passkey == "2PRK9HH#":
            st.session_state.authenticated = True
            st.success("✅ PASSWORD VALIDATED. ACCESS GRANTED.")
            st.rerun()
        else:
            st.error("❌ ACCESS DENIED: INVALID SYSTEM PASSKEY.")
            st.markdown(
                "> **RECOMMENDATION:** Please reach out to **AUTHOR 'CIZOR THE BADDEST' FOR ASSISTANCE**."
            )
    st.stop()

# --- INITIAL STATE MANAGEMENT ---
if "running" not in st.session_state:
    st.session_state.running = False
if "history" not in st.session_state:
    st.session_state.history = []

# --- INTERACTIVE DASHBOARD SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Core Parameters")
    st.markdown("**AUTHOR:** CIZOR THE BADDEST")
    
    app_id = st.text_input("App ID", value="1089")
    token = st.text_input("API Token", type="password")
    
    symbol = st.selectbox("Asset Index", ["1HZ10V", "1HZ25V", "1HZ50V", "1HZ75V", "1HZ100V"], 
                          help="Deriv Volatility Indices (1s Feed)")
    trade_type = st.radio("Trade Condition", ["DIGITUNDER", "DIGITOVER"])
    prediction = st.slider("Digit Prediction Target", 0, 9, 5)
    
    stake = st.number_input("Stake ($)", min_value=0.35, value=1.0, step=0.5)

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
balance_placeholder = m3.empty()
status_placeholder = m4.empty()

table_placeholder = st.empty()

# --- CORE TRADING ENGINE LOOP ---
async def trade_loop():
    url = f"wss://ws.derivws.com/websockets/v3?app_id={app_id}"
    
    async with websockets.connect(url) as ws:
        # Authenticate immediately
        auth_req = {"authorize": token}
        await ws.send(json.dumps(auth_req))
        auth_res = await ws.recv()
        auth_data = json.loads(auth_res)
        
        if "error" in auth_data:
            st.error(f"Auth Failed: {auth_data['error']['message']}")
            st.session_state.running = False
            return
            
        status_placeholder.metric("Engine Status", "Connected")
        balance_placeholder.metric("Account Balance", f"${float(auth_data['authorize']['balance']):,.2f}")

        # Subscribe to streaming updates
        tick_req = {"ticks": symbol}
        await ws.send(json.dumps(tick_req))
        
        while st.session_state.running:
            try:
                res = await ws.recv()
                data = json.loads(res)
                
                if "tick" in data:
                    tick_val = data["tick"]["quote"]
                    tick_str = f"{tick_val:.2f}"
                    last_digit = int(tick_str[-1])
                    
                    tick_placeholder.metric("Live Quote", tick_val)
                    last_digit_placeholder.metric("Last Digit", last_digit)
                    
                    # Execution logic block
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
                                "duration": 1,
                                "duration_unit": "t",
                                "prediction": prediction,
                                "symbol": symbol
                            }
                        }
                        await ws.send(json.dumps(contract_req))
                        
                elif "buy" in data:
                    if "error" in data:
                        st.sidebar.error(f"Execution Error: {data['error']['message']}")
                    else:
                        p_id = data["buy"]["contract_id"]
                        new_bal = data["buy"]["balance_after"]
                        balance_placeholder.metric("Account Balance", f"${float(new_bal):,.2f}")
                        
                        st.session_state.history.insert(0, {
                            "Timestamp": datetime.now().strftime("%H:%M:%S"),
                            "Contract ID": p_id,
                            "Symbol": symbol,
                            "Type": trade_type,
                            "Stake": f"${stake:.2f}"
                        })
                
                # Render clean execution summary table
                if st.session_state.history:
                    df = pd.DataFrame(st.session_state.history).head(15)
                    table_placeholder.dataframe(df, use_container_width=True)
                    
            except Exception as e:
                st.sidebar.error(f"Loop Exception: {str(e)}")
                break

# --- RUN LOOP GATE ---
if st.session_state.running:
    asyncio.run(trade_loop())
else:
    status_placeholder.metric("Engine Status", "Offline")