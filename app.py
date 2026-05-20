import streamlit as st
import asyncio
import websockets
import json
import ssl
import threading
import time
import pandas as pd
from datetime import datetime

# --- SYSTEM HEADER CONFIGURATION ---
st.set_page_config(page_title="CHITI Over/Under Bot", page_icon="⚡", layout="wide")

# Micro Layout CSS Injection: Squeezes margins and sizes text for a tight dashboard layout
st.markdown("""
    <style>
    .block-container {padding-top: 0.5rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
    h1, h2, h3 {margin-bottom: 0.1rem; margin-top: 0.1rem; font-size: 1.1rem !important;}
    div[data-testid="metric-container"] {background-color: #0d0d0d; padding: 0.15rem 0.4rem; border-radius: 4px; border: 1px solid #1a1a1a;}
    div[data-testid="stCodeBlock"] {margin-bottom: 0.1rem;}
    div[data-styled-df] {font-size: 0.85rem;}
    </style>
""", unsafe_allow_html=True)

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
            st.markdown("> **RECOMMENDATION:** Please reach out to **AUTHOR 'CIZOR THE BADDEST' FOR ASSISTANCE**.")
    st.stop()

# --- ASSET SYMBOL REGISTRY ---
MARKETS = {
    "Volatility 10 (1s)": "1HZ10V",
    "Volatility 25 (1s)": "1HZ25V",
    "Volatility 50 (1s)": "1HZ50V",
    "Volatility 75 (1s)": "1HZ75V",
    "Volatility 100 (1s)": "1HZ100V"
}

# --- PERSISTENT STATE MANAGEMENT ARCHITECTURE ---
state_defaults = {
    "running": False,
    "tracked_balance": 0.00,
    "total_trades": 0,
    "total_wins": 0,
    "total_losses": 0,
    "history": [],
    "current_action": "ENGINE INITIALIZED — TELEMETRY DISCONNECTED",
    "live_quote": 0.00,
    "last_digit": 0,
    "market_scores": {m: 0.0 for m in MARKETS.keys()},
    "digit_frequencies": {i: 0.0 for i in range(10)}
}

for key, val in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- INTERACTIVE DASHBOARD SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Core Parameters")
    st.markdown("**AUTHOR:** CIZOR THE BADDEST")
    st.markdown("---")
    
    app_id = st.text_input("App ID", value="1089")
    token = st.text_input("API Token", type="password")
    
    selected_market_name = st.selectbox("Active Stream Target", list(MARKETS.keys()))
    symbol = MARKETS[selected_market_name]
    
    trade_type = st.radio("Manual Overwrite Mode", ["DIGITUNDER", "DIGITOVER"])
    prediction = st.slider("Manual Target Prediction", 0, 9, 5)
    
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
                st.error("Missing Token!")
    with col2:
        if st.button("🛑 STOP BOT", use_container_width=True):
            st.session_state.running = False
            st.session_state.current_action = "EMERGENCY COLD HALT EXECUTED"

    if st.button("🧹 PURGE HUD STORAGE", use_container_width=True):
        st.session_state.total_trades = 0
        st.session_state.total_wins = 0
        st.session_state.total_losses = 0
        st.session_state.history.clear()
        st.session_state.current_action = "METRICS PURGED"
        st.rerun()

# --- HIGH-VISIBILITY METRIC STRIP (MICRO DISPLAY) ---
if st.session_state.running:
    st.markdown("### STATUS: 🟢 CHITI SNIPER ACTIVE & RUNNING")
else:
    st.markdown("### STATUS: 🔴 ENGINE IDLE / SYSTEM PAUSED")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f} USD")
m2.metric("Total Executions", st.session_state.total_trades)
m3.metric("Won Contracts", f"🟩 {st.session_state.total_wins}")
m4.metric("Lost Contracts", f"🟥 {st.session_state.total_losses}")
m5.metric("Live Ticker Feed", f"{st.session_state.live_quote:.2f} [{st.session_state.last_digit}]")

st.info(f"**🤖 ACTIVE CONSOLE LOG:** {st.session_state.current_action}")

# Split Layout Configuration (Left Matrix Analysis | Right Trade Ledger)
layout_left, layout_right = st.columns([4, 5])

with layout_left:
    st.markdown("### 📊 Distribution Spectrum")
    freq = st.session_state.digit_frequencies
    pointer = "".join([f"{' ▲ ' if i == st.session_state.last_digit else '   ':^5}" for i in range(10)])
    nums = "".join([f"{i:^5}" for i in range(10)])
    pcts = "".join([f"{f'{freq.get(i, 0.0):.0f}%':^5}" for i in range(10)])
    st.code(f"{pointer}\n{nums}\n{pcts}")
    
    st.markdown("### 🎯 Smart Market Scanner Recommendation")
    scores_df = pd.DataFrame([
        {"Market Asset": k, "Signal Intensity": f"{v:.1f}%"} 
        for k, v in sorted(st.session_state.market_scores.items(), key=lambda item: item[1], reverse=True)
    ])
    st.dataframe(scores_df, use_container_width=True, hide_index=True, height=180)

with layout_right:
    st.markdown("### 📜 Real-Time Ledger")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history).head(8)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.code("No trades logged in the current loop execution pipeline.")

# --- ASYNC BACKGROUND EXECUTION ROUTINES ---
async def trade_loop(app_id, token, symbol, risk_percentage, min_stake, selected_market_name):
    url = f"wss://ws.derivws.com/websockets/v3?app_id={app_id}"
    digit_window = []
    prev_balance = 0.0
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    async with websockets.connect(url, ssl=ssl_context) as ws:
        # Step 1: Session Authorization
        auth_req = {"authorize": token}
        await ws.send(json.dumps(auth_req))
        auth_res = await ws.recv()
        auth_data = json.loads(auth_res)
        
        if "error" in auth_data:
            st.session_state.current_action = f"❌ API REJECTION: {auth_data['error']['message']}"
            st.session_state.running = False
            return
            
        current_bal = float(auth_data["authorize"]["balance"])
        st.session_state.tracked_balance = current_bal
        prev_balance = current_bal
        
        # Step 2: Live Channels Registration (Ticks + Stream Account Balances)
        await ws.send(json.dumps({"ticks": symbol}))
        await ws.send(json.dumps({"balance": 1, "subscribe": 1}))
        
        st.session_state.current_action = "TELEMETRY LINK SECURED — DISPATCHING MATRIX RADAR"
        
        while st.session_state.running:
            try:
                res = await ws.recv()
                data = json.loads(res)
                
                # Dynamic Balance Variant Node Tracker
                if "balance" in data:
                    realtime_bal = float(data["balance"]["balance"])
                    diff = realtime_bal - prev_balance
                    
                    if abs(diff) > 0.001:
                        if diff > 0:
                            st.session_state.total_wins += 1
                            st.session_state.current_action = f"🟩 CONTRACT WON! Account Balance Growing: +${diff:.2f}"
                            if st.session_state.history:
                                st.session_state.history[0]["Outcome"] = "WIN"
                                st.session_state.history[0]["Net P/L"] = f"+${diff:.2f}"
                        else:
                            st.session_state.total_losses += 1
                            st.session_state.current_action = f"🟥 CONTRACT lost. Adjusting analytics parameters: -${abs(diff):.2f}"
                            if st.session_state.history:
                                st.session_state.history[0]["Outcome"] = "LOSS"
                                st.session_state.history[0]["Net P/L"] = f"-${abs(diff):.2f}"
                                
                        st.session_state.tracked_balance = realtime_bal
                        prev_balance = realtime_bal
                    continue
                
                # Zero-Delay Ticker Interceptor Block
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
                    
                    # Statistical Probabilities Aggregator
                    under_2 = freqs.get(0, 0) + freqs.get(1, 0)
                    under_3 = freqs.get(0, 0) + freqs.get(1, 0) + freqs.get(2, 0)
                    over_7 = freqs.get(8, 0) + freqs.get(9, 0)
                    over_8 = freqs.get(9, 0)
                    under_8 = sum([freqs.get(x, 0) for x in range(8)])
                    over_2 = sum([freqs.get(x, 0) for x in range(3, 10)])
                    
                    # Store Scanner Scores
                    st.session_state.market_scores[selected_market_name] = max(under_2, under_3, over_7, over_8, under_8, over_2)

                    target_type = None
                    target_pred = None
                    is_sure_trade = False
                    
                    # --- CHITI CORE MATHEMATICAL SMART STRATEGY SELECTION ---
                    # Tier 1 Setup: Sure Win Scenarios (Under 2,3,8 & Over 2,7,8)
                    if under_2 > 38.0 and digit in [0, 1]:
                        target_type, target_pred, is_sure_trade = "DIGITUNDER", 2, True
                    elif under_3 > 46.0 and digit in [0, 1, 2]:
                        target_type, target_pred, is_sure_trade = "DIGITUNDER", 3, True
                    elif over_8 > 22.0 and digit == 9:
                        target_type, target_pred, is_sure_trade = "DIGITOVER", 8, True
                    elif over_7 > 38.0 and digit in [8, 9]:
                        target_type, target_pred, is_sure_trade = "DIGITOVER", 7, True
                    
                    # Tier 2 Setup: High Frequency Scalps (Grows Small Accounts Sensitively)
                    elif under_8 > 66.0 and digit in [5, 6, 7]:
                        target_type, target_pred, is_sure_trade = "DIGITUNDER", 8, False
                    elif over_2 > 66.0 and digit in [2, 3, 4]:
                        target_type, target_pred, is_sure_trade = "DIGITOVER", 2, False

                    # Contract Placement Execution Pipeline
                    if target_type is not None:
                        # Compound Safety Risk Sizing
                        calc_stake = st.session_state.tracked_balance * (risk_percentage / 100.0)
                        base_stake = max(min_stake, round(calc_stake, 2))
                        
                        if is_sure_trade:
                            base_stake = round(base_stake * 1.5, 2)
                            st.session_state.current_action = f"🎯 SURE MATCH DETECTED! Compounding Stake Size to ${base_stake}"
                        else:
                            st.session_state.current_action = f"⚡ FREQUENCY POSITION EXECUTED: Position Stake at ${base_stake}"
                            
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
                        await ws.send(json.dumps(order))
                        buy_res = json.loads(await ws.recv())
                        
                        if "buy" in buy_res:
                            st.session_state.total_trades += 1
                            st.session_state.history.insert(0, {
                                "Timestamp": datetime.now().strftime("%H:%M:%S"),
                                "Contract ID": buy_res["buy"]["contract_id"],
                                "Setup Strategy": f"{target_type} {target_pred}",
                                "Intensity Profile": "🔥 SURE ACCUM" if is_sure_trade else "⚡ STANDARD",
                                "Risk Stake": f"${base_stake:.2f}",
                                "Outcome": "PROCESSING...",
                                "Net P/L": "$0.00"
                            })
                            await asyncio.sleep(1.5)  # Safe buffer to allow contract tick clearance
                            
            except Exception as e:
                st.session_state.current_action = f"⚠️ PIPELINE RE-ENTERING FLOW: {str(e)}"
                await asyncio.sleep(1)
                break

# --- MULTI-THREAD DISPATCH HANDLER ---
def run_async_loop_in_thread(app_id, token, symbol, risk_percentage, min_stake, selected_market_name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(trade_loop(app_id, token, symbol, risk_percentage, min_stake, selected_market_name))
    loop.close()

if st.session_state.running:
    active_threads = [t.name for t in threading.enumerate()]
    if "CHITI_ENGINE_WORKER" not in active_threads:
        worker = threading.Thread(
            target=run_async_loop_in_thread, 
            name="CHITI_ENGINE_WORKER",
            args=(app_id, token, symbol, risk_percentage, min_stake, selected_market_name),
            daemon=True
        )
        worker.start()

# --- CONTINUOUS UI REFRESH PING PIN ---
if st.session_state.running:
    time.sleep(0.1)
    st.rerun()