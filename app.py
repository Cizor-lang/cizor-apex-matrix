import streamlit as st
import json
import ssl
import websocket
import pandas as pd
import threading
import time
from datetime import datetime

# --- SYSTEM DASHBOARD HUD CONFIGURATION ---
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

# --- MARKET MAP REGISTRY ---
MARKETS = {
    "Volatility 10 (1s)": "1HZ10V",
    "Volatility 25 (1s)": "1HZ25V",
    "Volatility 50 (1s)": "1HZ50V",
    "Volatility 75 (1s)": "1HZ75V",
    "Volatility 100 (1s)": "1HZ100V"
}

# --- PERSISTENT LIFECYCLE ARRAY STATES ---
state_defaults = {
    "running": False,
    "tracked_balance": 0.00,
    "total_wins": 0,
    "total_losses": 0,
    "consecutive_losses": 0,
    "history": [],
    "active_contract_ids": set(),  # Tracks open tickets to prevent duplication
    "current_action": "ENGINE BOUND — ARCHITECTURE BALANCED",
    "live_quote": 0.00,
    "last_digit": 0,
    "digit_window": [],
    "cooldown_until": 0
}

for key, val in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- SYNCHRONIZED COUNTER CALCULATION ---
total_executions = st.session_state.total_wins + st.session_state.total_losses

# --- SIDEBAR CONTROL PANEL ---
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
    risk_percentage = st.slider("Dynamic Risk Profile (%)", min_value=1.0, max_value=20.0, value=2.0, step=0.5)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ START BOT", use_container_width=True):
            if token:
                st.session_state.running = True
                st.session_state.digit_window = []
                st.session_state.consecutive_losses = 0
                st.session_state.cooldown_until = 0
                st.session_state.active_contract_ids.clear()
                st.rerun()
            else:
                st.error("Enter API Token!")
    with col2:
        if st.button("🛑 STOP BOT", use_container_width=True):
            st.session_state.running = False
            st.session_state.current_action = "ENGINE SYSTEM PAUSED BY USER"
            st.rerun()

    if st.button("🧹 PURGE METRICS STORAGE", use_container_width=True):
        st.session_state.total_wins = 0
        st.session_state.total_losses = 0
        st.session_state.consecutive_losses = 0
        st.session_state.history.clear()
        st.session_state.active_contract_ids.clear()
        st.rerun()

# --- HUD DISPLAY CONTAINER MATRIX ---
st.markdown(f"### CHITI CORE MATRIX HUD: {'🟩 RUNNING' if st.session_state.running else '🟥 PAUSED'}")

m1, m2, m3, m4, m5 = st.columns(5)
balance_slot = m1.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f} USD")
trades_slot = m2.metric("Total Executions", total_executions)
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

# --- ISOLATED DISPATCH WORKER PIPELINE ---
def fire_synchronized_contract(url, token, base_stake, target_type, target_pred, symbol):
    try:
        dispatch_ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        dispatch_ws.connect(url)
        dispatch_ws.send(json.dumps({"authorize": token}))
        auth_raw = json.loads(dispatch_ws.recv())
        
        if "error" in auth_raw:
            return

        order = {
            "buy": 1,
            "price": float(base_stake),
            "parameters": {
                "amount": float(base_stake),
                "basis": "stake",
                "contract_type": target_type,  # Strict API enumerations
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
            c_id = buy_res["buy"]["contract_id"]
            st.session_state.active_contract_ids.add(c_id)
            timestamp_str = datetime.now().strftime("%H:%M:%S")
            st.session_state.history.insert(0, {
                "Timestamp": timestamp_str,
                "Contract ID": c_id,
                "Setup Strategy": f"{target_type} {target_pred}",
                "Stake Profile": f"${base_stake:.2f}",
                "Outcome": "PENDING TRANSACTION...",
                "Net P/L": "$0.00"
            })
    except Exception:
        pass

# --- MAIN EXECUTION FEED PIPELINE ---
if st.session_state.running:
    url = f"wss://ws.derivws.com/websockets/v3?app_id={app_id}"
    ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    
    try:
        ws.connect(url)
        ws.send(json.dumps({"authorize": token}))
        auth_res = json.loads(ws.recv())
        
        if "error" in auth_res:
            st.session_state.running = False
            st.rerun()
            
        st.session_state.tracked_balance = float(auth_res["authorize"]["balance"])
        balance_slot.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f} USD")
        
        # Subscribe to Real-Time Ticks + Strict Transaction Logging Stream
        ws.send(json.dumps({"ticks": symbol}))
        ws.send(json.dumps({"transaction": 1, "subscribe": 1}))
        
        while st.session_state.running:
            res = ws.recv()
            data = json.loads(res)
            
            # --- FIXED TRANSACTION PARSER NODE (ELIMINATES DOUBLE-COUNT RACE CONDITIONS) ---
            if "transaction" in data:
                tx = data["transaction"]
                contract_id = tx.get("contract_id")
                action = tx.get("action")  # "buy" or "sell"
                
                # Check if this contract belongs to our bot's active history array
                if contract_id in st.session_state.active_contract_ids and action == "sell":
                    profit = float(tx.get("profit", 0.00))
                    st.session_state.tracked_balance = float(tx.get("balance", st.session_state.tracked_balance))
                    
                    # Update metrics specifically matched to the individual settlement transaction ID
                    if profit > 0:
                        st.session_state.total_wins += 1
                        st.session_state.consecutive_losses = 0
                        outcome_str, pl_str = "🟢 WIN", f"+${profit:.2f}"
                    else:
                        st.session_state.total_losses += 1
                        st.session_state.consecutive_losses += 1
                        outcome_str, pl_str = "🔴 LOSS", f"-${abs(profit):.2f}"
                        
                        if st.session_state.consecutive_losses >= 2:
                            st.session_state.cooldown_until = time.time() + 15.0
                            st.session_state.consecutive_losses = 0
                    
                    # Update row layout inside the ledger
                    for row in st.session_state.history:
                        if row["Contract ID"] == contract_id:
                            row["Outcome"] = outcome_str
                            row["Net P/L"] = pl_str
                            break
                    
                    # Remove token from active memory set now that transaction lifecycle has concluded
                    st.session_state.active_contract_ids.remove(contract_id)
                    
                    # Rerender components cleanly without duplication updates
                    balance_slot.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f} USD")
                    wins_slot.metric("Won Contracts", f"🟩 {st.session_state.total_wins}")
                    losses_slot.metric("Lost Contracts", f"🟥 {st.session_state.total_losses}")
                    trades_slot.metric("Total Executions", st.session_state.total_wins + st.session_state.total_losses)
                    ledger_slot.dataframe(pd.DataFrame(st.session_state.history).head(10), use_container_width=True, hide_index=True)
                continue

            # --- LIVE TICK AGGREGATOR NODE ---
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
                
                # Circuit breaker status checker node
                if time.time() < st.session_state.cooldown_until:
                    rem = int(st.session_state.cooldown_until - time.time())
                    strategy_log_slot.warning(f"🛑 LOSS CIRCUIT BREAKER ENGAGED: Halting execution nodes for {rem}s...")
                    continue

                if len(st.session_state.digit_window) < 4:
                    strategy_log_slot.info("⚙️ Human Analyser: Syncing underlying market feed signature matrix...")
                    continue
                
                recent_ticks = st.session_state.digit_window[-4:]
                target_type = None
                target_pred = None
                reason = "Scanning digit wave anomalies..."

                # TARGET ANALYSIS CONFIRMATION WAVE CHECKS
                if recent_ticks[-1] in [0, 1] and recent_ticks[-2] in [0, 1, 2]:
                    target_type, target_pred = "DIGITUNDER", 8
                    reason = f"🎯 WAVE MATCHED: Low profile confirmed {recent_ticks[-2:]}. Executing UNDER 8 contract payload."
                elif recent_ticks[-1] == 2 and recent_ticks[-2] <= 3:
                    target_type, target_pred = "DIGITUNDER", 7
                    reason = f"⚡ WAVE MATCHED: Support pattern confirmed. Executing UNDER 7 contract payload."
                elif recent_ticks[-1] == 7 and recent_ticks[-2] >= 6:
                    target_type, target_pred = "DIGITOVER", 2
                    reason = f"⚡ WAVE MATCHED: Resistance pattern confirmed. Executing OVER 2 contract payload."
                elif recent_ticks[-1] in [8, 9] and recent_ticks[-2] in [7, 8, 9]:
                    target_type, target_pred = "DIGITOVER", 3
                    reason = f"🎯 WAVE MATCHED: High profile confirmed {recent_ticks[-2:]}. Executing OVER 3 contract payload."
                else:
                    reason = f"⏳ WAITING: Current pattern ({recent_ticks}) is tracking noise. Standing by for optimal setups."

                strategy_log_slot.info(f"**Engine Brain:** {reason}")

                if target_type is not None:
                    calc_stake = st.session_state.tracked_balance * (risk_percentage / 100.0)
                    base_stake = max(min_stake, round(calc_stake, 2))
                    
                    t = threading.Thread(
                        target=fire_synchronized_contract,
                        args=(url, token, base_stake, target_type, target_pred, symbol),
                        daemon=True
                    )
                    t.start()
                    
                    # Cool-down to wait for contract settlement safely
                    time.sleep(2.5)

    except Exception as e:
        st.session_state.running = False
        st.rerun()
else:
    strategy_log_slot.warning("Engine stopped. Press ▶️ START BOT to activate human-emulated trading.")
    if st.session_state.history:
        ledger_slot.dataframe(pd.DataFrame(st.session_state.history).head(10), use_container_width=True, hide_index=True)