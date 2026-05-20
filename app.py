import streamlit as st
import json
import ssl
import websocket
import pandas as pd
import threading
from datetime import datetime

# --- SYSTEM HUD CONFIGURATION ---
st.set_page_config(page_title="CHITI Over/Under Bot", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .block-container {padding-top: 0.4rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
    h1, h2, h3 {margin-bottom: 0.1rem; margin-top: 0.1rem; font-size: 1.1rem !important;}
    div[data-testid="metric-container"] {background-color: #0d0d0d; padding: 0.15rem 0.4rem; border-radius: 4px; border: 1px solid #1a1a1a;}
    div[data-testid="stCodeBlock"] {margin-bottom: 0.1rem;}
    </style>
""", unsafe_allow_html=True)

# --- SECURITY INTERCEPT GATEWAY ---
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

# --- LIFECYCLE MEMORY STATE ---
state_defaults = {
    "running": False,
    "tracked_balance": 0.00,
    "total_trades": 0,
    "total_wins": 0,
    "total_losses": 0,
    "history": [],
    "current_action": "ENGINE INITIALIZED — TELEMETRY ARMED",
    "live_quote": 0.00,
    "last_digit": 0,
    "digit_window": []
}

for key, val in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- INTERACTIVE CONTROL SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Core Parameters")
    st.markdown("**AUTHOR:** CIZOR THE BADDEST")
    st.markdown("---")
    app_id = st.text_input("App ID", value="1089")
    token = st.text_input("API Token", type="password")
    selected_market_name = st.selectbox("Active Stream Target", list(MARKETS.keys()))
    symbol = MARKETS[selected_market_name]
    
    st.markdown("---")
    st.markdown("**⚡ RISK ALLOCATIONS**")
    min_stake = st.number_input("System Minimum Stake ($)", min_value=0.35, value=0.50, step=0.05)
    risk_percentage = st.slider("Dynamic Risk Profile (%)", min_value=1.0, max_value=20.0, value=5.0, step=0.5)

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

# --- HIGH-VISIBILITY HUD CARD MATRIX ---
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

# --- THREADED ISOLATED BUY DISPATCHER ---
def async_order_dispatch(url, token, base_stake, target_type, target_pred, symbol):
    try:
        # Create a dedicated, clean connection just for executing the purchase order
        dispatch_ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        dispatch_ws.connect(url)
        dispatch_ws.send(json.dumps({"authorize": token}))
        json.loads(dispatch_ws.recv()) # Clear handshake response
        
        order = {
            "buy": 1,
            "price": base_stake,
            "parameters": {
                "amount": base_stake,
                "basis": "stake",
                "contract_type": target_type,
                "currency": "USD",
                "duration": 1,
                "duration_unit": "t",
                "prediction": target_pred,
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
                "Outcome": "EXECUTED",
                "Net P/L": "Pending Stream..."
            })
    except Exception:
        pass

# --- ACTIVE INTERCEPT CONTINUOUS PIPELINE ---
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
        
        # Subscribe to Real-Time Tickers and continuous balance broadcasts
        ws.send(json.dumps({"ticks": symbol}))
        ws.send(json.dumps({"balance": 1, "subscribe": 1}))
        
        prev_balance = st.session_state.tracked_balance
        
        while st.session_state.running:
            res = ws.recv()
            data = json.loads(res)
            
            # Real-Time Account Balance Delta Tracker
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

            # Real-Time Tick Stream Aggregator
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
                    
                win_len = len(st.session_state.digit_window)
                nums = "".join([f"{i:^5}" for i in range(10)])
                counts = "".join([f"{st.session_state.digit_window.count(i):^5}" for i in range(10)])
                spectrum_slot.code(f"Digits:     {nums}\nOccurrences:{counts}\nTotal Samples: {win_len}/15")
                
                # --- STRATEGY MAP: UNDER 7/8 AND OVER 2/3 ---
                target_type = None
                target_pred = None
                reason = "Scanning matrix..."

                # Match every single digit directly to maximize win probability and frequency
                if digit in [0, 1]:
                    target_type, target_pred = "DIGITUNDER", 8
                    reason = f"🎯 TICK [{digit}]: Maximizing probability safely. Executing UNDER 8 position."
                elif digit == 2:
                    target_type, target_pred = "DIGITUNDER", 7
                    reason = f"⚡ TICK [{digit}]: Frequency scalp target hit. Executing UNDER 7 position."
                elif digit in [3, 4, 5, 6]:
                    # Flat neutral middle zone split: alternate execution paths instantly to force trade volume
                    if digit % 2 == 0:
                        target_type, target_pred = "DIGITUNDER", 8
                        reason = f"⚡ TICK [{digit}]: Neutral Scalp split. Forcing high frequency UNDER 8 position."
                    else:
                        target_type, target_pred = "DIGITOVER", 2
                        reason = f"⚡ TICK [{digit}]: Neutral Scalp split. Forcing high frequency OVER 2 position."
                elif digit == 7:
                    target_type, target_pred = "DIGITOVER", 2
                    reason = f"⚡ TICK [{digit}]: Frequency scalp target hit. Executing OVER 2 position."
                elif digit in [8, 9]:
                    target_type, target_pred = "DIGITOVER", 3
                    reason = f"🎯 TICK [{digit}]: Maximizing probability safely. Executing OVER 3 position."

                strategy_log_slot.info(f"**Engine Brain:** {reason}")

                # Offload order execution to the thread pool so the tick counter never freezes
                if target_type is not None:
                    calc_stake = st.session_state.tracked_balance * (risk_percentage / 100.0)
                    base_stake = max(min_stake, round(calc_stake, 2))
                    
                    # Off-thread Dispatch execution 
                    t = threading.Thread(
                        target=async_order_dispatch,
                        args=(url, token, base_stake, target_type, target_pred, symbol),
                        daemon=True
                    )
                    t.start()
                    
                    # Update counts immediately
                    trades_slot.metric("Total Executions", st.session_state.total_trades)
                    if st.session_state.history:
                        ledger_slot.dataframe(pd.DataFrame(st.session_state.history).head(10), use_container_width=True, hide_index=True)

    except Exception as e:
        st.session_state.current_action = f"Pipeline reset: {str(e)}"
        st.session_state.running = False
        st.rerun()
else:
    strategy_log_slot.warning("Engine stopped. Press ▶️ START BOT to activate high-frequency scalper pipeline feeds.")
    if st.session_state.history:
        ledger_slot.dataframe(pd.DataFrame(st.session_state.history).head(10), use_container_width=True, hide_index=True)