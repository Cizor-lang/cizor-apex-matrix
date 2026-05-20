import streamlit as st
import json
import ssl
import time
import pandas as pd
import threading
from datetime import datetime
from websocket import create_connection

# --- SYSTEM CONFIGURATION ---
st.set_page_config(page_title="CHITI Sniper Engine v2", page_icon="⚡", layout="wide")

# --- PASSKEY SECURITY GATEWAY ---
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

# --- INITIAL THREAD-SAFE STATE ARCHITECTURE ---
MARKETS = {
    "Volatility 10 (1s)": "1HZ10V",
    "Volatility 25 (1s)": "1HZ25V",
    "Volatility 50 (1s)": "1HZ50V",
    "Volatility 75 (1s)": "1HZ75V",
    "Volatility 100 (1s)": "1HZ100V"
}

state_defaults = {
    "running": False,
    "tracked_balance": 0.00,
    "total_trades": 0,
    "total_wins": 0,
    "total_losses": 0,
    "history": [],
    "current_action": "SYSTEM INITIALIZED — RECONNAISSANCE ARMED",
    "live_quote": 0.00,
    "last_digit": 0,
    "market_scores": {m: 0.0 for m in MARKETS.keys()},
    "digit_frequencies": {i: 0.0 for i in range(10)}
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
    
    selected_market_name = st.selectbox("Active Stream Target", list(MARKETS.keys()))
    symbol = MARKETS[selected_market_name]
    
    st.markdown("---")
    st.markdown("**⚡ ALGORITHMIC ALLOCATIONS**")
    min_stake = st.number_input("System Minimum Stake ($)", min_value=0.35, value=0.35, step=0.05)
    risk_percentage = st.slider("Dynamic Risk Profile (%)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ START BOT", use_container_width=True):
            if token:
                st.session_state.running = True
            else:
                st.error("API Token Required")
    with col2:
        if st.button("🛑 STOP BOT", use_container_width=True):
            st.session_state.running = False
            st.session_state.current_action = "EMERGENCY HALT COMPLETED"

    if st.button("🧹 PURGE METRICS CACHE", use_container_width=True):
        st.session_state.total_trades = 0
        st.session_state.total_wins = 0
        st.session_state.total_losses = 0
        st.session_state.history.clear()
        st.session_state.current_action = "METRICS PURGED"
        st.rerun()

# --- CONTINUOUS BACKGROUND WORKER ENGINE ---
def websocket_worker(app_id, token, symbol, risk_percentage, min_stake):
    ws_url = f"wss://ws.derivws.com/websockets/v3?app_id={app_id}"
    digit_window = []
    prev_balance = 0.0
    
    try:
        ws = create_connection(ws_url, sslopt={"cert_reqs": ssl.CERT_NONE})
        
        # Immediate Account Authentication
        ws.send(json.dumps({"authorize": token}))
        auth_data = json.loads(ws.recv())
        if "error" in auth_data:
            st.session_state.current_action = f"❌ API REJECTION: {auth_data['error']['message']}"
            st.session_state.running = False
            return
            
        current_bal = float(auth_data["authorize"]["balance"])
        st.session_state.tracked_balance = current_bal
        prev_balance = current_bal
        
        # Synchronized Data Streams Subscriptions
        ws.send(json.dumps({"ticks": symbol}))
        ws.send(json.dumps({"balance": 1, "subscribe": 1}))
        
        st.session_state.current_action = "TELEMETRY LINK SECURED — MONITORING FLOWS"
        
        while st.session_state.running:
            raw_msg = ws.recv()
            data = json.loads(raw_msg)
            
            # 1. Real-Time Balance Interceptor
            if "balance" in data:
                realtime_bal = float(data["balance"]["balance"])
                diff = realtime_bal - prev_balance
                
                if abs(diff) > 0.001:
                    if diff > 0:
                        st.session_state.total_wins += 1
                        st.session_state.current_action = f"🟩 CONTRACT WON! Payout Balance Credited: +${diff:.2f}"
                        if st.session_state.history:
                            st.session_state.history[0]["Outcome"] = "WIN"
                            st.session_state.history[0]["Net P/L"] = f"+${diff:.2f}"
                    else:
                        st.session_state.total_losses += 1
                        st.session_state.current_action = f"🟥 CONTRACT LOST. Margin Deducted: -${abs(diff):.2f}"
                        if st.session_state.history:
                            st.session_state.history[0]["Outcome"] = "LOSS"
                            st.session_state.history[0]["Net P/L"] = f"-${abs(diff):.2f}"
                            
                    st.session_state.tracked_balance = realtime_bal
                    prev_balance = realtime_bal
                continue
                
            # 2. Continuous Tick Processing Node
            if "tick" in data:
                quote = float(data["tick"]["quote"])
                quote_str = f"{quote:.2f}"
                digit = int(quote_str[-1])
                
                st.session_state.live_quote = quote
                st.session_state.last_digit = digit
                
                digit_window.append(digit)
                if len(digit_window) > 40:
                    digit_window.pop(0)
                    
                total = len(digit_window)
                freqs = {i: (digit_window.count(i) / total) * 100 for i in range(10)}
                st.session_state.digit_frequencies = freqs
                
                # --- STRATEGY SIGNAL ROUTERS ---
                under_2 = freqs[0] + freqs[1]
                under_3 = freqs[0] + freqs[1] + freqs[2]
                over_7 = freqs[8] + freqs[9]
                over_8 = freqs[9]
                under_8 = sum([freqs[x] for x in range(8)])
                over_2 = sum([freqs[x] for x in range(3, 10)])
                
                # Dynamic Scoring Engine Updates
                st.session_state.market_scores[selected_market_name] = max(under_2, under_3, over_7, over_8, under_8, over_2)

                trade_type = None
                prediction = None
                is_sure_trade = False
                
                # Absolute Sniper Rules
                if under_2 > 35.0 and digit in [0, 1]:
                    trade_type, prediction, is_sure_trade = "DIGITUNDER", 2, True
                elif under_3 > 45.0 and digit in [0, 1, 2]:
                    trade_type, prediction, is_sure_trade = "DIGITUNDER", 3, True
                elif over_8_density := over_8 > 20.0 and digit == 9:
                    trade_type, prediction, is_sure_trade = "DIGITOVER", 8, True
                elif over_7 > 35.0 and digit in [8, 9]:
                    trade_type, prediction, is_sure_trade = "DIGITOVER", 7, True
                elif under_8 > 68.0 and digit in [5, 6, 7]:
                    trade_type, prediction, is_sure_trade = "DIGITUNDER", 8, False
                elif over_2 > 68.0 and digit in [2, 3, 4]:
                    trade_type, prediction, is_sure_trade = "DIGITOVER", 2, False

                # Trade Execution Block
                if trade_type is not None:
                    calc_stake = st.session_state.tracked_balance * (risk_percentage / 100.0)
                    base_stake = max(min_stake, round(calc_stake, 2))
                    
                    if is_sure_trade:
                        base_stake = round(base_stake * 1.5, 2)
                        st.session_state.current_action = f"🎯 SNIPER IMBALANCE TRIGGERED! Boosting Stake to ${base_stake}"
                    else:
                        st.session_state.current_action = f"⚡ STANDARD EXECUTION TRIGGERED: Placement Stake at ${base_stake}"
                        
                    order = {
                        "buy": 1,
                        "price": base_stake,
                        "parameters": {
                            "amount": base_stake,
                            "basis": "stake",
                            "contract_type": trade_type,
                            "currency": "USD",
                            "duration": 1,
                            "duration_unit": "t",
                            "prediction": prediction,
                            "symbol": symbol
                        }
                    }
                    ws.send(json.dumps(order))
                    buy_res = json.loads(ws.recv())
                    
                    if "buy" in buy_res:
                        st.session_state.total_trades += 1
                        st.session_state.history.insert(0, {
                            "Timestamp": datetime.now().strftime("%H:%M:%S"),
                            "Contract ID": buy_res["buy"]["contract_id"],
                            "Target Setup": f"{trade_type} {prediction}",
                            "Type": "SURE CONFIG" if is_sure_trade else "STANDARD",
                            "Stake Value": f"${base_stake:.2f}",
                            "Outcome": "PROCESSING...",
                            "Net P/L": "$0.00"
                        })
                        time.sleep(1.8) # Prevent overlapping execution states
                        
    except Exception as e:
        st.session_state.current_action = f"⚠️ WORKER DISCONNECTED: {str(e)}"
        st.session_state.running = False

# --- ACTIVATION AND LIFECYCLE MANAGEMENT ---
if st.session_state.running:
    # Ensure active execution threads do not duplicate stack layers
    active_threads = [t.name for t in threading.enumerate()]
    if "CHITI_ENGINE_WORKER" not in active_threads:
        worker = threading.Thread(
            target=websocket_worker, 
            name="CHITI_ENGINE_WORKER",
            args=(app_id, token, symbol, risk_percentage, min_stake),
            daemon=True
        )
        worker.start()

# --- HIGH-VISIBILITY HUD INTERFACE ---
col_status, col_blank = st.columns([2, 1])
with col_status:
    if st.session_state.running:
        st.markdown("### STATUS: 🟢 CHITI MATRIX ACTIVE & TRADING")
    else:
        st.markdown("### STATUS: 🔴 ENGINE IDLE / SYSTEM PAUSED")

# Unified Metrics Grid
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Real-Time Balance", f"${st.session_state.tracked_balance:,.2f} USD")
m2.metric("Total Executions", st.session_state.total_trades)
m3.metric("Won Contracts", f"🟩 {st.session_state.total_wins}")
m4.metric("Lost Contracts", f"🟥 {st.session_state.total_losses}")
m5.metric("Ticker Live Last Digit", f"{st.session_state.live_quote:.2f} [{st.session_state.last_digit}]")

# Core Action Hud Box
st.info(f"**🤖 ACTIVE CONSOLE ACTIVITY:** {st.session_state.current_action}")

# Dashboard Split Layout
layout_left, layout_right = st.columns([1, 2])

with layout_left:
    st.markdown("### 📊 Distribution Spectrum")
    freq = st.session_state.digit_frequencies
    pointer = "".join([f"{' ▲ ' if i == st.session_state.last_digit else '   ':^6}" for i in range(10)])
    nums = "".join([f"{i:^6}" for i in range(10)])
    pcts = "".join([f"{f'{freq.get(i, 0.0):.0f}%':^6}" for i in range(10)])
    st.code(f"{pointer}\n{nums}\n{pcts}")
    
    st.markdown("---")
    st.markdown("### 🎯 Live Market Screener Matrix")
    scores_df = pd.DataFrame([
        {"Market Asset": k, "Imbalance Signal Intensity": f"{v:.1f}%"} 
        for k, v in sorted(st.session_state.market_scores.items(), key=lambda item: item[1], reverse=True)
    ])
    st.dataframe(scores_df, use_container_width=True, hide_index=True)
    st.caption("ℹ️ Switch the sidebar configuration to whichever asset shows the highest signal intensity.")

with layout_right:
    st.markdown("### 📜 Real-Time Ledger")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history).head(12)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.code("No trades logged in the current session pipeline.")

# --- DYNAMIC INTERFACE UI REFRESH PIN ---
if st.session_state.running:
    time.sleep(0.1)
    st.rerun()