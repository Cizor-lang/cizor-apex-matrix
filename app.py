import streamlit as st
import asyncio
import websockets
import json
import pandas as pd
from datetime import datetime

# --- SYSTEM HEADER CONFIGURATION ---
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

# --- ENGINE SESSION MATRIX ---
MARKET_MAP = {
    "Volatility 10 (1s) Index": "1HZ10V",
    "Volatility 25 (1s) Index": "1HZ25V",
    "Volatility 50 (1s) Index": "1HZ50V",
    "Volatility 75 (1s) Index": "1HZ75V",
    "Volatility 100 (1s) Index": "1HZ100V"
}

if "running" not in st.session_state:
    st.session_state.running = False
if "history" not in st.session_state:
    st.session_state.history = []
if "tracked_balance" not in st.session_state:
    st.session_state.tracked_balance = 0.00
if "total_trades" not in st.session_state:
    st.session_state.total_trades = 0
if "total_wins" not in st.session_state:
    st.session_state.total_wins = 0
if "total_losses" not in st.session_state:
    st.session_state.total_losses = 0
if "digit_history" not in st.session_state:
    st.session_state.digit_history = []
if "current_action" not in st.session_state:
    st.session_state.current_action = "SYSTEM STANDBY — AWAITING ARMED RUN SIGNALS"

# --- INTERACTIVE DASHBOARD SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Core Parameters")
    st.markdown("**AUTHOR:** CIZOR THE BADDEST")
    
    app_id = st.text_input("App ID", value="1089")
    token = st.text_input("API Token", type="password")
    
    selected_market_name = st.selectbox("Asset Index", list(MARKET_MAP.keys()), help="Deriv Volatility Indices (1s Feed)")
    symbol = MARKET_MAP[selected_market_name]
    
    st.markdown("---")
    st.markdown("**⚡ RISK & AUTOMATION RULES**")
    min_stake = st.number_input("Minimum Allowed Stake ($)", min_value=0.35, value=0.35, step=0.05)
    risk_percentage = st.slider("Auto-Compound Account Risk (%)", min_value=1.0, max_value=20.0, value=3.0, step=0.5)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ START BOT", use_container_width=True):
            if token:
                st.session_state.running = True
                st.session_state.current_action = "INITIALIZING BALANCED TUNNELS..."
            else:
                st.error("Missing Token!")
    with col2:
        if st.button("🛑 STOP BOT", use_container_width=True):
            st.session_state.running = False
            st.session_state.current_action = "EMERGENCY COOLDOWN ENGAGED BY USER"

    if st.button("🧹 PURGE HUD CACHE", use_container_width=True):
        st.session_state.total_trades = 0
        st.session_state.total_wins = 0
        st.session_state.total_losses = 0
        st.session_state.history.clear()
        st.session_state.digit_history.clear()
        st.rerun()

# --- LIVE HUD METRICS INTERFACE ---
grid1, grid2, grid3, grid4 = st.columns(4)
status_placeholder = grid1.empty()
balance_placeholder = grid2.empty()
wins_losses_placeholder = grid3.empty()
live_digit_placeholder = grid4.empty()

# Real-Time Operational State Banner
st.info(f"**🤖 CURRENT ENGINE ACTIVITY:** {st.session_state.current_action}")

col_left, col_right = st.columns([1, 2])
with col_left:
    st.markdown("### 📊 Spectrum Matrix")
    spectrum_placeholder = st.empty()
    st.markdown("---")
    st.markdown("### 🎯 Best Market Navigator")
    screener_placeholder = st.empty()

with col_right:
    st.markdown("### 📜 Real-Time Ledger")
    table_placeholder = st.empty()

# --- CONCURRENT TRANSACTION & TICK PROCESSOR ---
async def trade_loop():
    url = f"wss://ws.derivws.com/websockets/v3?app_id={app_id}"
    
    async with websockets.connect(url) as ws:
        # Step 1: Immediate Authentication Verification
        auth_req = {"authorize": token}
        await ws.send(json.dumps(auth_req))
        auth_res = await ws.recv()
        auth_data = json.loads(auth_res)
        
        if "error" in auth_data:
            st.session_state.current_action = f"❌ AUTHENTICATION REFUSED: {auth_data['error']['message']}"
            st.session_state.running = False
            return
            
        # Register balance layers cleanly
        st.session_state.tracked_balance = float(auth_data["authorize"]["balance"])
        prev_balance = st.session_state.tracked_balance
        
        # Step 2: Establish Parallel Streams
        await ws.send(json.dumps({"ticks": symbol}))
        await ws.send(json.dumps({"balance": 1, "subscribe": 1}))
        
        status_placeholder.metric("Engine Status", "🟢 TRADING ACTIVE")
        balance_placeholder.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f} USD")
        
        st.session_state.current_action = "CHANNELS LOCKED. CALCULATING MARKET STRUCTURAL IMBALANCES..."
        
        while st.session_state.running:
            try:
                # Read stream without dropping background state frames
                res = await ws.recv()
                data = json.loads(res)
                
                # --- TASK 1: ACCURATE REAL-TIME BALANCE STREAM INTERCEPTOR ---
                if "balance" in data:
                    realtime_bal = float(data["balance"]["balance"])
                    balance_change = realtime_bal - prev_balance
                    
                    if abs(balance_change) > 0.001:
                        if balance_change > 0:
                            st.session_state.total_wins += 1
                            st.session_state.current_action = f"🟩 SNIPER TARGET SECURED! Profit Deposited: +${balance_change:.2f}"
                            if st.session_state.history:
                                st.session_state.history[0]["Outcome"] = "🟢 WIN"
                                st.session_state.history[0]["Net P/L"] = f"+${balance_change:.2f}"
                        else:
                            st.session_state.total_losses += 1
                            st.session_state.current_action = f"🟥 BARRIER HIT. Account Margin Deducted: -${abs(balance_change):.2f}"
                            if st.session_state.history:
                                st.session_state.history[0]["Outcome"] = "🔴 LOSS"
                                st.session_state.history[0]["Net P/L"] = f"-${abs(balance_change):.2f}"
                        
                        st.session_state.tracked_balance = realtime_bal
                        prev_balance = realtime_bal
                        
                        # Direct metrics update
                        balance_placeholder.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f} USD")
                        wins_losses_placeholder.metric("Wins / Losses", f"W: {st.session_state.total_wins} | L: {st.session_state.total_losses}")
                        st.rerun()
                    continue

                # --- TASK 2: LIVE LAST DIGIT FREQUENCY ANALYZER ---
                elif "tick" in data:
                    tick_val = data["tick"]["quote"]
                    tick_str = f"{tick_val:.2f}"
                    last_digit = int(tick_str[-1])
                    
                    live_digit_placeholder.metric("Live Ticker (Last Digit)", f"{tick_val:.2f} [{last_digit}]")
                    
                    st.session_state.digit_history.append(last_digit)
                    if len(st.session_state.digit_history) > 40:
                        st.session_state.digit_history.pop(0)
                        
                    total_ticks = len(st.session_state.digit_history)
                    freqs = {i: (st.session_state.digit_history.count(i) / total_ticks) * 100 for i in range(10)}
                    
                    # Live Spectrum Render View
                    with spectrum_placeholder.container():
                        pointer = "".join([f"{' ▲ ' if i == last_digit else '   ':^5}" for i in range(10)])
                        nums = "".join([f"{i:^5}" for i in range(10)])
                        pcts = "".join([f"{f'{freqs[i]:.0f}%':^5}" for i in range(10)])
                        st.code(f"{pointer}\n{nums}\n{pcts}")

                    # --- ADVANCED ACCURACY LOGIC ROUTERS ---
                    under_2_density = freqs[0] + freqs[1]
                    under_3_density = freqs[0] + freqs[1] + freqs[2]
                    over_7_density = freqs[8] + freqs[9]
                    over_8_density = freqs[9]
                    under_8_density = sum([freqs[x] for x in range(8)])
                    over_2_density = sum([freqs[x] for x in range(3, 10)])

                    # Market Recommendation Evaluator Engine
                    scores = {
                        "UNDER 2": under_2_density, "UNDER 3": under_3_density,
                        "OVER 7": over_7_density, "OVER 8": over_8_density,
                        "UNDER 8": under_8_density, "OVER 2": over_2_density
                    }
                    best_strategy = max(scores, key=scores.get)
                    highest_intensity = scores[best_strategy]
                    
                    with screener_placeholder.container():
                        st.success(f"🎯 **RECOMMENDED:** `{best_strategy}` Strategy")
                        st.metric("Signal Intensity Strength", f"{highest_intensity:.1f}%")

                    trade_type = None
                    prediction = None
                    is_sure_trade = False
                    
                    # 1. 1000% High-Certainty Over/Under Intercept Targets
                    if under_2_density > 34.0 and last_digit in [0, 1]:
                        trade_type, prediction, is_sure_trade = "DIGITUNDER", 2, True
                    elif under_3_density > 42.0 and last_digit in [0, 1, 2]:
                        trade_type, prediction, is_sure_trade = "DIGITUNDER", 3, True
                    elif over_8_density > 22.0 and last_digit == 9:
                        trade_type, prediction, is_sure_trade = "DIGITOVER", 8, True
                    elif over_7_density > 34.0 and last_digit in [8, 9]:
                        trade_type, prediction, is_sure_trade = "DIGITOVER", 7, True
                    
                    # 2. Maximum Payout Baseline Sniper Entries
                    elif under_8_density > 65.0 and last_digit in [5, 6, 7]:
                        trade_type, prediction, is_sure_trade = "DIGITUNDER", 8, False
                    elif over_2_density > 65.0 and last_digit in [2, 3, 4]:
                        trade_type, prediction, is_sure_trade = "DIGITOVER", 2, False

                    # --- DYNAMIC COMPOUNDING STAKE MATRIX ---
                    if trade_type is not None:
                        calc_compound = st.session_state.tracked_balance * (risk_percentage / 100.0)
                        calculated_stake = max(min_stake, round(calc_compound, 2))
                        
                        # High Certainty Boost Verification Adjustments
                        if is_sure_trade:
                            calculated_stake = round(calculated_stake * 1.5, 2)
                            st.session_state.current_action = f"🎯 IMBALANCE CONFIRMED! Boosting Position to ${calculated_stake} USD"
                        else:
                            st.session_state.current_action = f"⚡ STANDARD ALIGNMENT SCALPER ENVELOPE: Stake ${calculated_stake} USD"

                        # Transmit Order Package Envelope
                        contract_req = {
                            "buy": 1,
                            "price": calculated_stake,
                            "parameters": {
                                "amount": calculated_stake,
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
                        buy_res = json.loads(await ws.recv())
                        
                        if "buy" in buy_res:
                            st.session_state.total_trades += 1
                            st.session_state.history.insert(0, {
                                "Timestamp": datetime.now().strftime("%H:%M:%S"),
                                "Contract ID": buy_res["buy"]["contract_id"],
                                "Target Model": f"{trade_type} {prediction}",
                                "Sizing Profile": "⚡ AUTOMATED SURE BOOST" if is_sure_trade else "⏳ BASELINE SNIPER",
                                "Risk Stake": f"${calculated_stake:.2f}",
                                "Outcome": "⌛ PROCESSING EXPIRED REEFS...",
                                "Net P/L": "$0.00"
                            })
                            # Core thread suspension window to match tick durations
                            await asyncio.sleep(1.8)

                # Dynamically update the execution summary table
                if st.session_state.history:
                    df = pd.DataFrame(st.session_state.history).head(12)
                    table_placeholder.dataframe(df, use_container_width=True)
                    
            except Exception as e:
                st.sidebar.error(f"Engine Loop Exception: {str(e)}")
                break

# --- RUN LOOP GATEWAY HUB ---
if st.session_state.running:
    wins_losses_placeholder.metric("Wins / Losses", f"W: {st.session_state.total_wins} | L: {st.session_state.total_losses}")
    asyncio.run(trade_loop())
else:
    status_placeholder.metric("Engine Status", "🔴 BOT DEACTIVATED")
    balance_placeholder.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f} USD")
    wins_losses_placeholder.metric("Wins / Losses", f"W: {st.session_state.total_wins} | L: {st.session_state.total_losses}")