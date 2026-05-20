import streamlit as st
import asyncio
import websockets
import json
import pandas as pd
import math
from datetime import datetime

# --- SYSTEM CONFIGURATION ---
st.set_page_config(page_title="CHITI Sniper Engine", page_icon="⚡", layout="wide")

# --- INITIAL PASSKEY SECURITY GATEWAY ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 CIZOR APEX INTERCEPT GATEWAY")
    st.markdown("---")
    
    input_passkey = st.text_input("ENTER OPERATIONAL PASSKEY:", type="password")
    release_btn = st.button("🚀 ENGAGE CORE SYSTEM")
    
    if release_btn:
        if input_passkey == "2PRK9HH#":
            st.session_state.authenticated = True
            st.success("✅ PASSWORD VALIDATED. ACCESS GRANTED.")
            st.rerun()
        else:
            st.error("❌ ACCESS DENIED: INVALID SYSTEM PASSKEY.")
            st.markdown("> **RECOMMENDATION:** Please reach out to **AUTHOR 'CIZOR THE BADDEST' FOR ASSISTANCE**.")
    st.stop()

# --- COMPREHENSIVE ENGINE STATE ENGINE MATRIX ---
state_defaults = {
    "running": False,
    "tracked_balance": 0.00,
    "prev_balance": 0.00,
    "total_trades": 0,
    "total_wins": 0,
    "total_losses": 0,
    "digit_history": [],
    "history": [],
    "current_action": "SYSTEM IDLE — AWAITING START COMMAND",
    "last_digit": 0,
    "live_quote": 0.00,
    "last_contract_id": None
}

for key, val in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- INTERACTIVE CONTROL PANEL ---
with st.sidebar:
    st.header("⚙️ Sniper Configuration")
    st.markdown("**ENGINE AUTHOR:** CIZOR THE BADDEST")
    st.markdown("---")
    
    app_id = st.text_input("Deriv App ID", value="1089")
    token = st.text_input("API Token", type="password")
    
    symbol = st.selectbox(
        "Asset Index Target", 
        ["1HZ10V", "1HZ25V", "1HZ50V", "1HZ75V", "1HZ100V"],
        format_func=lambda x: f"Volatility {x.replace('1HZ', '').replace('V', '')} (1s) Index"
    )
    
    st.markdown("---")
    st.markdown("**⚡ ALGORITHMIC BALANCING PARAMETERS**")
    min_stake = st.number_input("System Minimum Stake ($)", min_value=0.35, value=0.35, step=0.05)
    risk_percentage = st.slider("Dynamic Standard Allocation (%)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ START ENGINE", use_container_width=True):
            if token:
                st.session_state.running = True
                st.session_state.current_action = "INITIALIZING RADAR TUNNELS..."
            else:
                st.error("API Token Required")
    with col2:
        if st.button("🛑 STOP ENGINE", use_container_width=True):
            st.session_state.running = False
            st.session_state.current_action = "EMERGENCY HALT EXECUTED BY OWNER"

    if st.button("🧹 PURGE METRICS CACHE", use_container_width=True):
        st.session_state.total_trades = 0
        st.session_state.total_wins = 0
        st.session_state.total_losses = 0
        st.session_state.history.clear()
        st.session_state.digit_history.clear()
        st.rerun()

# --- HIGH-VISIBILITY TELEMETRY INTERFACE ---
status_color = "🟢 RUNNING & ARMED" if st.session_state.running else "🔴 DEACTIVATED / OFFLINE"
st.subheader(f"System Status: {status_color}")

# Telemetry Metrics Grid
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f} USD")
m2.metric("Total Executions", st.session_state.total_trades)
m3.metric("Won Contracts", f"🟩 {st.session_state.total_wins}")
m4.metric("Lost Contracts", f"🟥 {st.session_state.total_losses}")
m5.metric("Ticker [Last Digit]", f"{st.session_state.live_quote:.2f} [{st.session_state.last_digit}]")

# Live Engine Status Log Box
st.info(f"**🤖 CURRENT ENGINE ACTIVITY:** {st.session_state.current_action}")

# Layout Separation
left_col, right_col = st.columns([1, 2])
with left_col:
    st.markdown("### 📊 Distribution Spectrum")
    spectrum_placeholder = st.empty()

with right_col:
    st.markdown("### 📜 Real-Time Ledger")
    table_placeholder = st.empty()

# --- ASYNC MULTIPLEX TRADING CORE ENGINE ---
async def main_trading_system():
    url = f"wss://ws.derivws.com/websockets/v3?app_id={app_id}"
    
    async with websockets.connect(url) as ws:
        # Step 1: Secure Server Authorization
        await ws.send(json.dumps({"authorize": token}))
        auth_data = json.loads(await ws.recv())
        
        if "error" in auth_data:
            st.session_state.current_action = f"❌ AUTHENTICATION ERROR: {auth_data['error']['message']}"
            st.session_state.running = False
            return
            
        st.session_state.tracked_balance = float(auth_data["authorize"]["balance"])
        st.session_state.prev_balance = st.session_state.tracked_balance
        
        # Step 2: Establish Parallel Event Channels (Ticks + Continuous Account Balances)
        await ws.send(json.dumps({"ticks": symbol}))
        await ws.send(json.dumps({"balance": 1, "subscribe": 1}))
        
        st.session_state.current_action = "TUNNELS REINFORCED. SCANNING DISTRIBUTION WAVE DENSITIES..."
        
        while st.session_state.running:
            try:
                # Capture websocket messages without network lockups
                message = await asyncio.wait_for(ws.recv(), timeout=0.1)
                data = json.loads(message)
                
                # --- CHANNEL 1: LIVE ACCOUNT BALANCE PROCESSING ---
                if "balance" in data:
                    realtime_bal = float(data["balance"]["balance"])
                    diff = realtime_bal - st.session_state.prev_balance
                    
                    if abs(diff) > 0.001:
                        if diff > 0:
                            st.session_state.total_wins += 1
                            st.session_state.current_action = f"🟩 TARGET CONTRACT SECURED! +${diff:.2f} DEPOSITED."
                            if st.session_state.history:
                                st.session_state.history[0]["Outcome"] = "🟢 WIN"
                                st.session_state.history[0]["Net Return"] = f"+${diff:.2f}"
                        else:
                            st.session_state.total_losses += 1
                            st.session_state.current_action = f"🟥 BARRIER DEFLECTION. -${abs(diff):.2f} ADJUSTING MULTIPLIERS."
                            if st.session_state.history:
                                st.session_state.history[0]["Outcome"] = "🔴 LOSS"
                                st.session_state.history[0]["Net Return"] = f"-${abs(diff):.2f}"
                        
                        st.session_state.tracked_balance = realtime_bal
                        st.session_state.prev_balance = realtime_bal
                        st.rerun()

                # --- CHANNEL 2: ZERO-DELAY STREAM TICK INTERCEPTION ---
                elif "tick" in data:
                    quote = float(data["tick"]["quote"])
                    quote_str = f"{quote:.2f}"
                    digit = int(quote_str[-1])
                    
                    st.session_state.live_quote = quote
                    st.session_state.last_digit = digit
                    st.session_state.digit_history.append(digit)
                    
                    if len(st.session_state.digit_history) > 30:
                        st.session_state.digit_history.pop(0)
                        
                    # Frequency calculations
                    total = len(st.session_state.digit_history)
                    freq = {i: (st.session_state.digit_history.count(i) / total) * 100 for i in range(10)}
                    
                    # Update Visualizer Density Chart cleanly
                    with spectrum_placeholder.container():
                        pointer = "".join([f"{' ▲ ' if i == digit else '   ':^6}" for i in range(10)])
                        nums = "".join([f"{i:^6}" for i in range(10)])
                        pcts = "".join([f"{f'{freq[i]:.0f}%':^6}" for i in range(10)])
                        st.code(f"{pointer}\n{nums}\n{pcts}")

                    # --- STRATEGY PROFILE MATRIX ---
                    # 1000% Density Rules
                    under_2_density = freq[0] + freq[1]
                    under_3_density = freq[0] + freq[1] + freq[2]
                    over_7_density = freq[8] + freq[9]
                    over_8_density = freq[9]
                    
                    # Standard Sniper Rules
                    under_8_density = sum([freq[x] for x in range(8)])
                    over_2_density = sum([freq[x] for x in range(3, 10)])

                    selected_type = None
                    selected_prediction = None
                    is_sure_trade = False
                    
                    # Core Priority Scanning Logic
                    if under_2_density > 35.0 and digit in [0, 1]:
                        selected_type, selected_prediction, is_sure_trade = "DIGITUNDER", 2, True
                    elif under_3_density > 45.0 and digit in [0, 1, 2]:
                        selected_type, selected_prediction, is_sure_trade = "DIGITUNDER", 3, True
                    elif over_8_density > 20.0 and digit == 9:
                        selected_type, selected_prediction, is_sure_trade = "DIGITOVER", 8, True
                    elif over_7_density > 35.0 and digit in [8, 9]:
                        selected_type, selected_prediction, is_sure_trade = "DIGITOVER", 7, True
                    elif under_8_density > 65.0 and digit in [5, 6, 7]:
                        selected_type, selected_prediction, is_sure_trade = "DIGITUNDER", 8, False
                    elif over_2_density > 65.0 and digit in [2, 3, 4]:
                        selected_type, selected_prediction, is_sure_trade = "DIGITOVER", 2, False

                    # Execution block
                    if selected_type is not None and st.session_state.running:
                        # Auto-compounding account sizing rule
                        calc_stake = (st.session_state.tracked_balance * (risk_percentage / 100.0))
                        base_execution_stake = max(min_stake, round(calc_stake, 2))
                        
                        # Apply specialized boost multiplier for high certainty configurations
                        if is_sure_trade:
                            base_execution_stake = round(base_execution_stake * 1.5, 2)
                            st.session_state.current_action = f"🎯 SNIPER IMBALANCE FOUND! COMPREHENSIVE STAKE ENHANCED TO ${base_execution_stake} USD"
                        else:
                            st.session_state.current_action = f"⚡ RUNNING STANDARD CONTEXT ALIGNMENT CONTRACT STAKE: ${base_execution_stake} USD"
                        
                        # Generate Execution Envelope Payload
                        order_packet = {
                            "buy": 1,
                            "price": base_execution_stake,
                            "parameters": {
                                "amount": base_execution_stake,
                                "basis": "stake",
                                "contract_type": selected_type,
                                "currency": "USD",
                                "duration": 1,
                                "duration_unit": "t",
                                "prediction": selected_prediction,
                                "symbol": symbol
                            }
                        }
                        
                        await ws.send(json.dumps(order_packet))
                        buy_response = json.loads(await ws.recv())
                        
                        if "buy" in buy_response:
                            st.session_state.total_trades += 1
                            st.session_state.history.insert(0, {
                                "Timestamp": datetime.now().strftime("%H:%M:%S"),
                                "Contract ID": buy_response["buy"]["contract_id"],
                                "Setup Strategy": f"{selected_type} {selected_prediction}",
                                "Type": "🔥 HIGH ACCURACY SURGE" if is_sure_trade else "⚡ BASIC SNIPER",
                                "Risk Stake": f"${base_execution_stake:.2f}",
                                "Outcome": "⌛ PROCESSING EXPIRED REEFS...",
                                "Net Return": "$0.00"
                            })
                            # Short cooldown to match tick generation windows cleanly
                            await asyncio.sleep(1.8)

                # --- UPDATE INTERFACE FRAME ---
                if st.session_state.history:
                    df = pd.DataFrame(st.session_state.history).head(10)
                    table_placeholder.dataframe(df, use_container_width=True)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                st.session_state.current_action = f"⚠️ SYSTEM CONNECTION FAULT: {str(e)}"
                await asyncio.sleep(2)
                break

# --- ACTIVE INJECTION BRIDGE ---
if st.session_state.running:
    asyncio.run(main_trading_system())