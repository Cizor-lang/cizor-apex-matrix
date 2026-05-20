import streamlit as st
import json
import ssl
import websocket
import pandas as pd
import threading
import time
from datetime import datetime

# --- SYSTEM HUD DESIGN SKIN ---
st.set_page_config(page_title="CHITI Over/Under Bot", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .block-container {padding-top: 0.4rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
    h1, h2, h3 {margin-bottom: 0.1rem; margin-top: 0.1rem; font-size: 1.1rem !important;}
    div[data-testid="metric-container"] {background-color: #0d0d0d; padding: 0.15rem 0.4rem; border-radius: 4px; border: 1px solid #1a1a1a;}
    div[data-testid="stCodeBlock"] {margin-bottom: 0.1rem;}
    </style>
""", unsafe_allow_html=True)

# --- SECURITY GATEWAY INTERCEPT ---
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

# --- MARKET REGISTRY ---
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
    "total_trades": 0,
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

# --- CONTROLS SIDEBAR ---
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
    risk_percentage = st.slider("Dynamic Risk Sizing (%)", min_value=1.0, max_value=20.0, value=5.0, step=0.5)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ START BOT", use_container_width=True):
            if token:
                st.session_state.running = True
                st.session_state.digit_window = []
                st.rerun()
            else:
                st.error("Enter API Token!")
    with col2:
        if st.button("🛑 STOP BOT", use_container_width=True):
            st.session_state.running = False
            st.session_state.current_action = "ENGINE SYSTEM PAUSED BY USER"
            st.rerun()

    if st.button("🧹 PURGE METRICS STORAGE", use_container_width=True):
        st.session_state.total_trades = 0
        st.session_state.total_wins = 0
        st.session_state.total_losses = 0
        st.session_state.history.clear()
        st.rerun()

# --- HIGH-VISIBILITY DASHBOARD DISPLAYS ---
st.markdown(f"### CHITI SCALPER MATRIX: {'🟩 OPERATIONAL' if st.session_state.running else '🟥 PAUSED'}")

m1, m2, m3, m4, m5 = st.columns(5)
balance_slot = m1.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f} USD")
trades_slot = m2.metric("Total Executions", st.session_state.total_trades)
wins_slot = m3.metric("Won Contracts", f"🟩 {st.session_state.total_wins}")
losses_slot = m4.metric("Lost Contracts", f"🟥 {st.session_state.total_losses}")
ticker_slot = m5.metric("Live Ticker Feed", f"{st.session_state.live_quote:.2f} [{st.session_state.last_digit}]")

st.markdown("### 🎯 Real-Time Strategy Evaluation Scanner")
strategy_log_slot = st.empty()

layout_left, layout_right = st.columns([4, 5])
with layout_left:
    st.markdown("### 📊 Distribution Spectrum (Last 15 Ticks)")
    spectrum_slot = st.empty()
with layout_right:
    st.markdown("### 📜 Real-Time Ledger")
    ledger_slot = st.empty()

# --- TARGET BROKER DISPATCH PIPELINE WORKER ---
def execute_broker_trade(url, token, base_stake, target_type, target_pred, symbol):
    try:
        dispatch_ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        dispatch_ws.connect(url)
        
        # Authenticate contract lane
        dispatch_ws.send(json.dumps({"authorize": token}))
        auth_raw = dispatch_ws.recv()
        
        # CORRECT DERIV PROPOSAL SPECIFICATION MAP
        # For Over trades, contract_type MUST be "DIGITMATCH" and barrier sets prediction target
        contract_string = "DIGITMATCH" if target_type == "DIGITOVER" else "DIGITUNDER"
        
        order = {
            "buy": 1,
            "price": base_stake,
            "parameters": {
                "amount": base_stake,
                "basis": "stake",
                "contract_type": contract_string,
                "currency": "USD",
                "duration": 1,
                "duration_unit": "t",
                "barrier": str(target_pred),
                "symbol": symbol
            }
        }
        
        dispatch_ws.send(json.dumps(order))
        buy_res = json.loads(dispatch_ws.recv())
        dispatch_ws.close()
        
        if "buy" in buy_res:
            st.session_state.total_trades += 1
            st.session_state.history.insert(0, {
                "Timestamp": datetime.now().strftime("%H:%M:%S"),
                "Contract ID": buy_res["buy"]["contract_id"],
                "Setup": f"{target_type} {target_pred}",
                "Stake Value": f"${base_stake:.2f}",
                "Outcome": "PROCESSING",
                "Net P/L": "$0.00"
            })
        elif "error" in buy_res:
            st.session_state.current_action = f"❌ Broker Rejected: {buy_res['error']['message']}"
            
    except Exception as e:
        st.session_state.current_action = f"⚠️ Dispatch Exception: {str(e)}"

# --- MAIN SYNCHRONOUS FEED RUNNER LOOP ---
if st.session_state.running:
    url = f"wss://ws.derivws.com/websockets/v3?app_id={app_id}"
    ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    
    try:
        ws.connect(url)
        ws.send(json.dumps({"authorize": token}))
        auth_res = json.loads(ws.recv())
        
        if "error" in auth_res:
            st.session_state.current_action = f"Error: {auth_res['error']['message']}"
            st.session_state.running = False
            st.rerun()
            
        st.session_state.tracked_balance = float(auth_res["authorize"]["balance"])
        balance_slot.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f} USD")
        
        ws.send(json.dumps({"ticks": symbol}))
        ws.send(json.dumps({"balance": 1, "subscribe": 1}))
        
        prev_balance = st.session_state.tracked_balance
        tick_counting_buffer = 0
        
        while st.session_state.running:
            res = ws.recv()
            data = json.loads(res)
            
            # Balance Broadcast Monitoring
            if "balance" in data:
                new_bal = float(data["balance"]["balance"])
                diff = new_bal - prev_balance
                if abs(diff) > 0.001:
                    if diff > 0:
                        st.session_state.total_wins += 1
                        if st.session_state.history:
                            st.session_state.history[0]["Outcome"] = "🟢 WIN"
                            st.session_state.history[0]["Net P/L"] = f"+${diff:.2f}"
                    else:
                        st.session_state.total_losses += 1
                        if st.session_state.history:
                            st.session_state.history[0]["Outcome"] = "🔴 LOSS"
                            st.session_state.history[0]["Net P/L"] = f"-${abs(diff):.2f}"
                    
                    st.session_state.tracked_balance = new_bal
                    prev_balance = new_bal
                    
                    balance_slot.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f} USD")
                    wins_slot.metric("Won Contracts", f"🟩 {st.session_state.total_wins}")
                    losses_slot.metric("Lost Contracts", f"🟥 {st.session_state.total_losses}")
                    if st.session_state.history:
                        ledger_slot.dataframe(pd.DataFrame(st.session_state.history).head(10), use_container_width=True, hide_index=True)
                continue

            # Live Feed Tracking Handler
            if "tick" in data:
                quote = float(data["tick"]["quote"])
                quote_str = f"{quote:.2f}"
                digit = int(quote_str[-1])
                
                st.session_state.live_quote = quote
                st.session_state.last_digit = digit
                ticker_slot.metric("Live Ticker Feed", f"{quote:.2f} [{digit}]")
                
                st.session_state.digit_window.append(digit)
                if len(st.session_state.digit_window) > 15:
                    st.session_state.digit_window.pop(0)
                
                # Render historical chart updates
                win_len = len(st.session_state.digit_window)
                nums = "".join([f"{i:^5}" for i in range(10)])
                counts = "".join([f"{st.session_state.digit_window.count(i):^5}" for i in range(10)])
                spectrum_slot.code(f"Digits:     {nums}\nOccurrences:{counts}\nTotal Samples: {win_len}/15")
                
                # --- HUMAN SCALPER EMULATION ARCHITECTURE ---
                # Accumulate a small window buffer (e.g. 4 ticks) before performing professional evaluation
                tick_counting_buffer += 1
                if tick_counting_buffer < 4:
                    strategy_log_slot.info(f"**Engine Status:** ⏳ Human Analyser: Buffering tick velocity patterns ({tick_counting_buffer}/4)...")
                    continue
                
                # Reset counter and begin deep targeted execution scan
                tick_counting_buffer = 0
                target_type = None
                target_pred = None
                reason = "Evaluating spectrum variations..."

                # TARGET SCALPING WINDOW FOCUS: UNDER 7, 8 & OVER 2, 3
                if digit in [0, 1, 2]:
                    target_type, target_pred = "DIGITUNDER", 8
                    reason = f"🎯 ANALYSER: Low digit [{digit}] confirmed. Entering optimized UNDER 8 contract."
                elif digit == 3:
                    target_type, target_pred = "DIGITUNDER", 7
                    reason = f"⚡ ANALYSER: Support digit [{digit}] confirmed. Entering highly frequent UNDER 7 contract."
                elif digit in [4, 5]:
                    reason = f"⏳ ANALYSER: Mid-zone bracket [{digit}]. Re-evaluating subsequent ticks to avoid choppy data."
                elif digit == 6:
                    target_type, target_pred = "DIGITOVER", 2
                    reason = f"⚡ ANALYSER: Resistance digit [{digit}] confirmed. Entering highly frequent OVER 2 contract."
                elif digit in [7, 8, 9]:
                    target_type, target_pred = "DIGITOVER", 3
                    reason = f"🎯 ANALYSER: High digit [{digit}] confirmed. Entering optimized OVER 3 contract."

                strategy_log_slot.info(f"**Engine Status:** {reason} | **Console Alert:** {st.session_state.current_action}")

                # Fire Threaded Order Delivery
                if target_type is not None:
                    calc_stake = st.session_state.tracked_balance * (risk_percentage / 100.0)
                    base_stake = max(min_stake, round(calc_stake, 2))
                    
                    t = threading.Thread(
                        target=execute_broker_trade,
                        args=(url, token, base_stake, target_type, target_pred, symbol),
                        daemon=True
                    )
                    t.start()
                    
                    # Force safety sleep to block overlaps and act like a real human cooling down
                    time.sleep(2.0)
                    
                    trades_slot.metric("Total Executions", st.session_state.total_trades)
                    if st.session_state.history:
                        ledger_slot.dataframe(pd.DataFrame(st.session_state.history).head(10), use_container_width=True, hide_index=True)

    except Exception as e:
        st.session_state.current_action = f"Network Resetting: {str(e)}"
        st.session_state.running = False
        st.rerun()
else:
    strategy_log_slot.warning("Engine stopped. Press ▶️ START BOT to activate high-frequency human-emulated trading.")
    if st.session_state.history:
        ledger_slot.dataframe(pd.DataFrame(st.session_state.history).head(10), use_container_width=True, hide_index=True)