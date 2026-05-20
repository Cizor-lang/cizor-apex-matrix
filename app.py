import streamlit as st
import asyncio
import websockets
import json
import pandas as pd
from datetime import datetime

# --- SYSTEM HEADER CONFIGURATION (FIXED PARAMETER) ---
st.set_page_config(page_title="CHITI Sniper Engine v2", page_icon="⚡", layout="wide")

# Micro CSS layout optimizer (FIXED: Uses correct native parameter unsafe_allow_html)
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem; padding-left: 2rem; padding-right: 2rem;}
    h1, h2, h3 {margin-bottom: 0.1rem; margin-top: 0.1rem;}
    div[data-testid="metric-container"] {background-color: #111; padding: 0.3rem 0.6rem; border-radius: 4px; border: 1px solid #222;}
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
            st.markdown(
                "> **RECOMMENDATION:** Please reach out to **AUTHOR 'CIZOR THE BADDEST' FOR ASSISTANCE**."
            )
    st.stop()

# --- INITIAL SYSTEM STATE MATRIX ---
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
    "current_action": "SYSTEM ARMED — SCREENING SPECTRUMS",
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
    
    st.markdown("---")
    st.markdown("**⚡ ALGORITHMIC ALLOCATIONS**")
    min_stake = st.number_input("System Minimum Stake ($)", min_value=0.35, value=0.35, step=0.05)
    risk_percentage = st.slider("Dynamic Risk Profile (%)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)

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

# --- DYNAMIC MICRO HUD DISPLAY MAP ---
if st.session_state.running:
    st.markdown("### STATUS: 🟢 CHITI MATRIX ACTIVE & TRADING")
else:
    st.markdown("### STATUS: 🔴 ENGINE IDLE / SYSTEM PAUSED")

m1, m2, m3, m4, m5 = st.columns(5)
balance_placeholder = m1.empty()
trades_placeholder = m2.empty()
wins_placeholder = m3.empty()
losses_placeholder = m4.empty()
tick_placeholder = m5.empty()

st.info(f"**🤖 CURRENT ENGINE ACTIVITY:** {st.session_state.current_action}")

layout_left, layout_right = st.columns([2, 3])
with layout_left:
    st.markdown("### 📊 Distribution Spectrum")
    spectrum_placeholder = st.empty()
    st.markdown("### 🎯 Live Market Screener Matrix")
    screener_placeholder = st.empty()

with layout_right:
    st.markdown("### 📜 Real-Time Ledger")
    table_placeholder = st.empty()

# --- ASYNC HIGH-FREQUENCY EXECUTION CORE ---
async def trade_loop():
    url = f"wss://ws.derivws.com/websockets/v3?app_id={app_id}"
    digit_window = []
    
    async with websockets.connect(url) as ws:
        # Step 1: Immediate Account Session Authorization
        auth_req = {"authorize": token}
        await ws.send(json.dumps(auth_req))
        auth_res = await ws.recv()
        auth_data = json.loads(auth_res)
        
        if "error" in auth_data:
            st.sidebar.error(f"Auth Failed: {auth_data['error']['message']}")
            st.session_state.running = False
            return
            
        # Register immediate entry balance metrics
        st.session_state.tracked_balance = float(auth_data["authorize"]["balance"])
        balance_placeholder.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f} USD")
        
        # Step 2: Subscribe to Concurrent Channels (Tick Stream + Account Updates)
        await ws.send(json.dumps({"ticks": symbol}))
        await ws.send(json.dumps({"balance": 1, "subscribe": 1}))
        
        st.session_state.current_action = "TELEMETRY LINK SECURED — SCANNING VELOCITIES..."
        
        while st.session_state.running:
            try:
                res = await ws.recv()
                data = json.loads(res)
                
                # Channel A: Real-Time Balance Variance Processing Node
                if "balance" in data:
                    new_bal = float(data["balance"]["balance"])
                    diff = new_bal - st.session_state.tracked_balance
                    
                    if abs(diff) > 0.001:
                        if diff > 0:
                            st.session_state.total_wins += 1
                            st.session_state.current_action = f"🟩 TARGET SECURED! Balance Credited: +${diff:.2f}"
                            if st.session_state.history:
                                st.session_state.history[0]["Outcome"] = "🟢 WIN"
                                st.session_state.history[0]["Net P/L"] = f"+${diff:.2f}"
                        else:
                            st.session_state.total_losses += 1
                            st.session_state.current_action = f"🟥 BARRIER HIT. Balance Deducted: -${abs(diff):.2f}"
                            if st.session_state.history:
                                st.session_state.history[0]["Outcome"] = "🔴 LOSS"
                                st.session_state.history[0]["Net P/L"] = f"-${abs(diff):.2f}"
                                
                        st.session_state.tracked_balance = new_bal
                        balance_placeholder.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f} USD")
                        wins_placeholder.metric("Won Contracts", f"🟩 {st.session_state.total_wins}")
                        losses_placeholder.metric("Lost Contracts", f"🟥 {st.session_state.total_losses}")

                # Channel B: Zero-Delay Market Ticker Interception Node
                elif "tick" in data:
                    tick_val = data["tick"]["quote"]
                    tick_str = f"{tick_val:.2f}"
                    last_digit = int(tick_str[-1])
                    
                    st.session_state.live_quote = tick_val
                    st.session_state.last_digit = last_digit
                    
                    # Update dynamic viewports
                    tick_placeholder.metric("Live Last Digit", f"{tick_val:.2f} [{last_digit}]")
                    trades_placeholder.metric("Total Executions", st.session_state.total_trades)
                    wins_placeholder.metric("Won Contracts", f"🟩 {st.session_state.total_wins}")
                    losses_placeholder.metric("Lost Contracts", f"🟥 {st.session_state.total_losses}")
                    
                    digit_window.append(last_digit)
                    if len(digit_window) > 40:
                        digit_window.pop(0)
                        
                    total_ticks = len(digit_window)
                    freqs = {i: (digit_window.count(i) / total_ticks) * 100 for i in range(10)}
                    st.session_state.digit_frequencies = freqs
                    
                    # Calculate Signal Spectra Densities
                    under_2 = freqs.get(0, 0) + freqs.get(1, 0)
                    under_3 = freqs.get(0, 0) + freqs.get(1, 0) + freqs.get(2, 0)
                    over_7 = freqs.get(8, 0) + freqs.get(9, 0)
                    over_8 = freqs.get(9, 0)
                    under_8 = sum([freqs.get(x, 0) for x in range(8)])
                    over_2 = sum([freqs.get(x, 0) for x in range(3, 10)])
                    
                    # Update screener metric score
                    st.session_state.market_scores[selected_market_name] = max(under_2, under_3, over_7, over_8, under_8, over_2)
                    
                    # Live Visual Spectrum Render
                    pointer_str = "".join([f"{' ▲ ' if i == last_digit else '   ':^6}" for i in range(10)])
                    nums_str = "".join([f"{i:^6}" for i in range(10)])
                    pcts_str = "".join([f"{f'{freqs.get(i, 0.0):.0f}%':^6}" for i in range(10)])
                    spectrum_placeholder.code(f"{pointer_str}\n{nums_str}\n{pcts_str}")
                    
                    # Live Recommendation Box Render
                    scores_df = pd.DataFrame([
                        {"Market Index": k, "Signal Intensity": f"{v:.1f}%"} 
                        for k, v in sorted(st.session_state.market_scores.items(), key=lambda item: item[1], reverse=True)
                    ])
                    screener_placeholder.dataframe(scores_df, use_container_width=True, hide_index=True)
                    
                    # --- CORE ALGORITHMIC CONFIRMATION DEPLOYMENT MATRIX ---
                    trade_type = None
                    prediction = None
                    is_sure_trade = False
                    
                    if under_2 > 38.0 and last_digit in [0, 1]:
                        trade_type, prediction, is_sure_trade = "DIGITUNDER", 2, True
                    elif under_3 > 46.0 and last_digit in [0, 1, 2]:
                        trade_type, prediction, is_sure_trade = "DIGITUNDER", 3, True
                    elif over_8 > 22.0 and last_digit == 9:
                        trade_type, prediction, is_sure_trade = "DIGITOVER", 8, True
                    elif over_7 > 38.0 and last_digit in [8, 9]:
                        trade_type, prediction, is_sure_trade = "DIGITOVER", 7, True
                    elif under_8 > 66.0 and last_digit in [5, 6, 7]:
                        trade_type, prediction, is_sure_trade = "DIGITUNDER", 8, False
                    elif over_2 > 66.0 and last_digit in [2, 3, 4]:
                        trade_type, prediction, is_sure_trade = "DIGITOVER", 2, False
                        
                    # Execute Calculated Contract Positions
                    if trade_type is not None:
                        # Auto-Compounding Account Sizing Formula
                        calc_stake = st.session_state.tracked_balance * (risk_percentage / 100.0)
                        base_stake = max(min_stake, round(calc_stake, 2))
                        
                        if is_sure_trade:
                            base_stake = round(base_stake * 1.5, 2)
                            st.session_state.current_action = f"🎯 SURE MATCH DEPLOYED! Compounding Stake Size to ${base_stake}"
                        else:
                            st.session_state.current_action = f"⚡ PLACING SCALPER POSITION: Stake at ${base_stake}"
                            
                        contract_req = {
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
                        await ws.send(json.dumps(contract_req))
                        
                elif "buy" in data:
                    if "error" in data:
                        st.session_state.current_action = f"⚠️ GATEWAY REJECTION: {data['error']['message']}"
                    else:
                        st.session_state.total_trades += 1
                        p_id = data["buy"]["contract_id"]
                        st.session_state.history.insert(0, {
                            "Timestamp": datetime.now().strftime("%H:%M:%S"),
                            "Contract ID": p_id,
                            "Target Setup": f"{trade_type if 'trade_type' in locals() else 'EXEC'} {prediction if 'prediction' in locals() else ''}",
                            "Condition": "🔥 SURE TRADE" if ( 'is_sure_trade' in locals() and is_sure_trade ) else "⚡ SNIPER",
                            "Risk Stake": f"${base_stake:.2f}" if 'base_stake' in locals() else f"${min_stake:.2f}",
                            "Outcome": "⌛ EXECUTING...",
                            "Net P/L": "$0.00"
                        })
                        
                # Update ledger dataframe view cleanly without redraw latency
                if st.session_state.history:
                    df = pd.DataFrame(st.session_state.history).head(10)
                    table_placeholder.dataframe(df, use_container_width=True, hide_index=True)
                    
            except Exception as e:
                st.session_state.current_action = f"⚠️ PIPELINE LATENCY EXCEPTION: {str(e)}"
                await asyncio.sleep(1)
                break

# --- CONDITIONAL RUN ENGINE GATEWAYS ---
if st.session_state.running:
    asyncio.run(trade_loop())
else:
    balance_placeholder.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f} USD")
    trades_placeholder.metric("Total Executions", st.session_state.total_trades)
    wins_placeholder.metric("Won Contracts", f"🟩 {st.session_state.total_wins}")
    losses_placeholder.metric("Lost Contracts", f"🟥 {st.session_state.total_losses}")
    tick_placeholder.metric("Live Last Digit", "Offline")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history).head(10)
        table_placeholder.dataframe(df, use_container_width=True, hide_index=True)
    else:
        table_placeholder.code("System offline. Awaiting activation parameters from sidebar.")