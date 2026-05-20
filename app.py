import streamlit as st
import json
import ssl
import websocket
import pandas as pd
from datetime import datetime

# --- SYSTEM HEADER CONFIGURATION ---
st.set_page_config(page_title="CHITI Over/Under Bot", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .block-container {padding-top: 0.4rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
    h1, h2, h3 {margin-bottom: 0.1rem; margin-top: 0.1rem; font-size: 1.1rem !important;}
    div[data-testid="metric-container"] {background-color: #0d0d0d; padding: 0.15rem 0.4rem; border-radius: 4px; border: 1px solid #1a1a1a;}
    div[data-testid="stCodeBlock"] {margin-bottom: 0.1rem;}
    </style>
""", unsafe_allow_html=True)

# --- SECURITY GATEWAY ---
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

# --- MARKETS ---
MARKETS = {
    "Volatility 10 (1s)": "1HZ10V",
    "Volatility 25 (1s)": "1HZ25V",
    "Volatility 50 (1s)": "1HZ50V",
    "Volatility 75 (1s)": "1HZ75V",
    "Volatility 100 (1s)": "1HZ100V"
}

# --- LIFECYCLE STATE ---
state_defaults = {
    "running": False,
    "tracked_balance": 0.00,
    "total_trades": 0,
    "total_wins": 0,
    "total_losses": 0,
    "history": [],
    "current_action": "ENGINE ONLINE — READY",
    "live_quote": 0.00,
    "last_digit": 0,
    "digit_window": [],
    "market_scores": {m: 0.0 for m in MARKETS.keys()}
}

for key, val in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

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
    st.markdown("**⚡ RISK CONTROLS**")
    min_stake = st.number_input("System Minimum Stake ($)", min_value=0.35, value=0.50, step=0.05)
    risk_percentage = st.slider("Dynamic Risk Profile (%)", min_value=1.0, max_value=15.0, value=5.0, step=0.5)

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
            st.session_state.current_action = "ENGINE SHUTDOWN EXECUTED"
            st.rerun()

    if st.button("扫 PURGE DATA", use_container_width=True):
        st.session_state.total_trades = 0
        st.session_state.total_wins = 0
        st.session_state.total_losses = 0
        st.session_state.history.clear()
        st.rerun()

# --- HIGH-VISIBILITY DASHBOARD HUD ---
st.markdown(f"### SYSTEM HUD: {'🟩 RUNNING' if st.session_state.running else '🟥 STOPPED'}")

m1, m2, m3, m4, m5 = st.columns(5)
balance_slot = m1.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f}")
trades_slot = m2.metric("Total Executions", st.session_state.total_trades)
wins_slot = m3.metric("Won Contracts", f"🟩 {st.session_state.total_wins}")
losses_slot = m4.metric("Lost Contracts", f"🟥 {st.session_state.total_losses}")
ticker_slot = m5.metric("Live Ticket Feed", f"{st.session_state.live_quote:.2f} [{st.session_state.last_digit}]")

# Core Strategy Scanner Window
st.markdown("### 🎯 Live Mathematical Evaluation & Strategy Scanner")
strategy_log_slot = st.empty()

layout_left, layout_right = st.columns([4, 5])
with layout_left:
    st.markdown("### 📊 Last 15 Digits Analysis")
    spectrum_slot = st.empty()
with layout_right:
    st.markdown("### 📜 Real-Time Execution Ledger")
    ledger_slot = st.empty()

# --- SYNCHRONOUS BLOCK-FREE WEBSOCKET RUNNER ---
if st.session_state.running:
    url = f"wss://ws.derivws.com/websockets/v3?app_id={app_id}"
    ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    
    try:
        ws.connect(url)
        # 1. Authorize
        ws.send(json.dumps({"authorize": token}))
        auth_res = json.loads(ws.recv())
        
        if "error" in auth_res:
            st.session_state.current_action = f"Error: {auth_res['error']['message']}"
            st.session_state.running = False
            st.rerun()
            
        st.session_state.tracked_balance = float(auth_res["authorize"]["balance"])
        balance_slot.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f}")
        
        # 2. Subscribe to Feeds
        ws.send(json.dumps({"ticks": symbol}))
        ws.send(json.dumps({"balance": 1, "subscribe": 1}))
        
        prev_balance = st.session_state.tracked_balance
        
        # Active blocking bypass loop inside a simple rendering container
        while st.session_state.running:
            res = ws.recv()
            data = json.loads(res)
            
            # Intercept account balance notifications instantly
            if "balance" in data:
                new_bal = float(data["balance"]["balance"])
                diff = new_bal - prev_balance
                if abs(diff) > 0.001:
                    if diff > 0:
                        st.session_state.total_wins += 1
                        if st.session_state.history:
                            st.session_state.history[0]["Outcome"] = "WIN"
                            st.session_state.history[0]["Net P/L"] = f"+${diff:.2f}"
                    else:
                        st.session_state.total_losses += 1
                        if st.session_state.history:
                            st.session_state.history[0]["Outcome"] = "LOSS"
                            st.session_state.history[0]["Net P/L"] = f"-${abs(diff):.2f}"
                    
                    st.session_state.tracked_balance = new_bal
                    prev_balance = new_bal
                    
                    balance_slot.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f}")
                    wins_slot.metric("Won Contracts", f"🟩 {st.session_state.total_wins}")
                    losses_slot.metric("Lost Contracts", f"🟥 {st.session_state.total_losses}")
                    if st.session_state.history:
                        ledger_slot.dataframe(pd.DataFrame(st.session_state.history).head(10), use_container_width=True, hide_index=True)
                continue

            # Process live ticks
            if "tick" in data:
                quote = float(data["tick"]["quote"])
                quote_str = f"{quote:.2f}"
                digit = int(quote_str[-1])
                
                st.session_state.live_quote = quote
                st.session_state.last_digit = digit
                
                ticker_slot.metric("Live Ticker Feed", f"{quote:.2f} [{digit}]")
                
                # Append to math window
                st.session_state.digit_window.append(digit)
                if len(st.session_state.digit_window) > 15:
                    st.session_state.digit_window.pop(0)
                    
                # Render frequency visual display
                win_len = len(st.session_state.digit_window)
                nums = "".join([f"{i:^5}" for i in range(10)])
                counts = "".join([f"{st.session_state.digit_window.count(i):^5}" for i in range(10)])
                spectrum_slot.code(f"Digits:     {nums}\nOccurrences:{counts}\nTotal Samples: {win_len}/15")
                
                # High frequency calculation parameters
                last_3 = st.session_state.digit_window[-3:] if win_len >= 3 else st.session_state.digit_window
                
                # TARGET STRATEGY EVALUATION BLOCK
                target_type = None
                target_pred = None
                reason = "Scanning for matching patterns..."
                
                # Strategy logic checks
                if all(x < 5 for x in last_3) and len(last_3) == 3:
                    target_type, target_pred = "DIGITUNDER", 8
                    reason = "🔥 HIGH FREQUENCY CONFIRMED: Last 3 ticks were small numbers (Under 5). Buying UNDER 8."
                elif all(x > 4 for x in last_3) and len(last_3) == 3:
                    target_type, target_pred = "DIGITOVER", 2
                    reason = "🔥 HIGH FREQUENCY CONFIRMED: Last 3 ticks were large numbers (Over 4). Buying OVER 2."
                elif digit in [0, 1, 2]:
                    target_type, target_pred = "DIGITUNDER", 3
                    reason = f"⚡ SCALPER HIT: Tick isolated at [{digit}]. Taking highly probable UNDER 3."
                elif digit in [7, 8, 9]:
                    target_type, target_pred = "DIGITOVER", 7
                    reason = f"⚡ SCALPER HIT: Tick isolated at [{digit}]. Taking highly probable OVER 7."
                else:
                    reason = f"⏳ Neutral Zone: Digit [{digit}] does not hit high probability limits. Skipping tick to protect balance."

                strategy_log_slot.info(f"**Engine Brain:** {reason}")

                # Send execution request immediately if a target maps out
                if target_type is not None:
                    calc_stake = st.session_state.tracked_balance * (risk_percentage / 100.0)
                    base_stake = max(min_stake, round(calc_stake, 2))
                    
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
                    ws.send(json.dumps(order))
                    buy_res = json.loads(ws.recv())
                    
                    if "buy" in buy_res:
                        st.session_state.total_trades += 1
                        st.session_state.history.insert(0, {
                            "Timestamp": datetime.now().strftime("%H:%M:%S"),
                            "Contract ID": buy_res["buy"]["contract_id"],
                            "Setup": f"{target_type} {target_pred}",
                            "Stake": f"${base_stake:.2f}",
                            "Outcome": "PROCESSING...",
                            "Net P/L": "$0.00"
                        })
                        trades_slot.metric("Total Executions", st.session_state.total_trades)
                        ledger_slot.dataframe(pd.DataFrame(st.session_state.history).head(10), use_container_width=True, hide_index=True)
                        
    except Exception as e:
        st.session_state.current_action = f"Disconnected/Error: {str(e)}"
        st.session_state.running = False
        st.rerun()
else:
    strategy_log_slot.warning("Engine Engine stopped. Click ▶️ START BOT to activate trading feeds.")
    if st.session_state.history:
        ledger_slot.dataframe(pd.DataFrame(st.session_state.history).head(10), use_container_width=True, hide_index=True)