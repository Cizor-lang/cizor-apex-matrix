import streamlit as st
import asyncio
import websockets
import json
import ssl
import pandas as pd
from datetime import datetime

# --- SYSTEM HEADER CONFIGURATION ---
st.set_page_config(page_title="CHITI Over/Under Bot", page_icon="⚡", layout="wide")

# Micro Layout CSS Injection: Forces elements tightly together to maximize screener real estate
st.markdown("""
    <style>
    .block-container {padding-top: 0.4rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
    h1, h2, h3 {margin-bottom: 0.1rem; margin-top: 0.1rem; font-size: 1.1rem !important;}
    div[data-testid="metric-container"] {background-color: #0d0d0d; padding: 0.15rem 0.4rem; border-radius: 4px; border: 1px solid #1a1a1a;}
    div[data-testid="stCodeBlock"] {margin-bottom: 0.1rem;}
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

# --- STATE LIFECYCLE RE-ENGINEERING ---
state_defaults = {
    "running": False,
    "tracked_balance": 0.00,
    "total_trades": 0,
    "total_wins": 0,
    "total_losses": 0,
    "history": [],
    "current_action": "SYSTEM ONLINE — AWAITING RUN PARAMETERS",
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

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ START BOT", use_container_width=True):
            if token:
                st.session_state.running = True
                st.rerun()
            else:
                st.error("Missing Token!")
    with col2:
        if st.button("🛑 STOP BOT", use_container_width=True):
            st.session_state.running = False
            st.session_state.current_action = "EMERGENCY COLD HALT EXECUTED"
            st.rerun()

    if st.button("🧹 PURGE HUD STORAGE", use_container_width=True):
        st.session_state.total_trades = 0
        st.session_state.total_wins = 0
        st.session_state.total_losses = 0
        st.session_state.history.clear()
        st.session_state.current_action = "METRICS PURGED"
        st.rerun()

# --- HIGH-SPEED ENGINE SURFACE (THE NATIVE FRAGMENT FRONTIER) ---
@st.fragment
def render_and_execute_engine():
    # Structural Layout Render Block
    if st.session_state.running:
        st.markdown("### STATUS: 🟢 CHITI SNIPER ENGINE MATRIX ACTIVE & EXECULATING TRADES")
    else:
        st.markdown("### STATUS: 🔴 ENGINE IDLE / SYSTEM PAUSED")

    m1, m2, m3, m4, m5 = st.columns(5)
    balance_slot = m1.empty()
    trades_slot = m2.empty()
    wins_slot = m3.empty()
    losses_slot = m4.empty()
    ticker_slot = m5.empty()

    # Pre-populate fields immediately upon paint routine
    balance_slot.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f} USD")
    trades_slot.metric("Total Executions", st.session_state.total_trades)
    wins_slot.metric("Won Contracts", f"🟩 {st.session_state.total_wins}")
    losses_slot.metric("Lost Contracts", f"🟥 {st.session_state.total_losses}")
    ticker_slot.metric("Live Ticker Feed", f"{st.session_state.live_quote:.2f} [{st.session_state.last_digit}]")

    console_slot = st.empty()
    console_slot.info(f"**🤖 ACTIVE CONSOLE LOG:** {st.session_state.current_action}")

    layout_left, layout_right = st.columns([4, 5])
    with layout_left:
        st.markdown("### 📊 Distribution Spectrum")
        spectrum_slot = st.empty()
        st.markdown("### 🎯 Smart Market Scanner Recommendation")
        screener_slot = st.empty()

    with layout_right:
        st.markdown("### 📜 Real-Time Ledger")
        ledger_slot = st.empty()

    # Dynamic fallback loops for initial interface arrays
    freq = st.session_state.digit_frequencies
    pointer = "".join([f"{' ▲ ' if i == st.session_state.last_digit else '   ':^5}" for i in range(10)])
    nums = "".join([f"{i:^5}" for i in range(10)])
    pcts = "".join([f"{f'{freq.get(i, 0.0):.0f}%':^5}" for i in range(10)])
    spectrum_slot.code(f"{pointer}\n{nums}\n{pcts}")

    scores_df = pd.DataFrame([{"Market Asset": k, "Signal Intensity": f"{v:.1f}%"} for k, v in st.session_state.market_scores.items()])
    screener_slot.dataframe(scores_df, use_container_width=True, hide_index=True, height=150)
    
    if st.session_state.history:
        ledger_slot.dataframe(pd.DataFrame(st.session_state.history).head(8), use_container_width=True, hide_index=True)
    else:
        ledger_slot.code("No trades logged in the current loop execution pipeline.")

    # --- IN-LINE HIGH FREQUENCY ASYNC WORKER CORE ---
    async def async_worker():
        url = f"wss://ws.derivws.com/websockets/v3?app_id={app_id}"
        digit_window = []
        prev_balance = st.session_state.tracked_balance
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with websockets.connect(url, ssl=ssl_context) as ws:
            # Step 1: Secure Account Handshake Authentication
            await ws.send(json.dumps({"authorize": token}))
            auth_res = await ws.recv()
            auth_data = json.loads(auth_res)
            
            if "error" in auth_data:
                st.session_state.current_action = f"❌ API REJECTION: {auth_data['error']['message']}"
                console_slot.error(f"**🤖 ACTIVE CONSOLE LOG:** {st.session_state.current_action}")
                st.session_state.running = False
                return
                
            current_bal = float(auth_data["authorize"]["balance"])
            st.session_state.tracked_balance = current_bal
            prev_balance = current_bal
            balance_slot.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f} USD")
            
            # Step 2: Establish Direct Intercept Pipeline Streams
            await ws.send(json.dumps({"ticks": symbol}))
            await ws.send(json.dumps({"balance": 1, "subscribe": 1}))
            
            st.session_state.current_action = "TELEMETRY LINK SECURED — DISPATCHING MATRIX RADAR"
            console_slot.info(f"**🤖 ACTIVE CONSOLE LOG:** {st.session_state.current_action}")
            
            while st.session_state.running:
                res = await ws.recv()
                data = json.loads(res)
                
                # Account Sizing Balance Stream Node Detector
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
                            st.session_state.current_action = f"🟥 CONTRACT LOST. Adjusting parameters: -${abs(diff):.2f}"
                            if st.session_state.history:
                                st.session_state.history[0]["Outcome"] = "LOSS"
                                st.session_state.history[0]["Net P/L"] = f"-${abs(diff):.2f}"
                                
                        st.session_state.tracked_balance = realtime_bal
                        prev_balance = realtime_bal
                        
                        balance_slot.metric("Account Balance", f"${st.session_state.tracked_balance:,.2f} USD")
                        wins_slot.metric("Won Contracts", f"🟩 {st.session_state.total_wins}")
                        losses_slot.metric("Lost Contracts", f"🟥 {st.session_state.total_losses}")
                        console_slot.info(f"**🤖 ACTIVE CONSOLE LOG:** {st.session_state.current_action}")
                        if st.session_state.history:
                            ledger_slot.dataframe(pd.DataFrame(st.session_state.history).head(8), use_container_width=True, hide_index=True)
                    continue

                # Live High-Frequency Tick Streams
                if "tick" in data:
                    quote = float(data["tick"]["quote"])
                    quote_str = f"{quote:.2f}"
                    digit = int(quote_str[-1])
                    
                    st.session_state.live_quote = quote
                    st.session_state.last_digit = digit
                    
                    ticker_slot.metric("Live Ticker Feed", f"{quote:.2f} [{digit}]")
                    trades_slot.metric("Total Executions", st.session_state.total_trades)
                    
                    digit_window.append(digit)
                    if len(digit_window) > 40:
                        digit_window.pop(0)
                        
                    total = len(digit_window)
                    freqs = {i: (digit_window.count(i) / total) * 100 for i in range(10)}
                    st.session_state.digit_frequencies = freqs
                    
                    # Statistical Signal Intensity Real-time Calculations
                    under_2 = freqs.get(0, 0) + freqs.get(1, 0)
                    under_3 = freqs.get(0, 0) + freqs.get(1, 0) + freqs.get(2, 0)
                    over_7 = freqs.get(8, 0) + freqs.get(9, 0)
                    over_8 = freqs.get(9, 0)
                    under_8 = sum([freqs.get(x, 0) for x in range(8)])
                    over_2 = sum([freqs.get(x, 0) for x in range(3, 10)])
                    
                    st.session_state.market_scores[selected_market_name] = max(under_2, under_3, over_7, over_8, under_8, over_2)
                    
                    # Update Spectrum and Screener Widgets Live
                    p_str = "".join([f"{' ▲ ' if i == digit else '   ':^5}" for i in range(10)])
                    n_str = "".join([f"{i:^5}" for i in range(10)])
                    pct_str = "".join([f"{f'{freqs.get(i, 0.0):.0f}%':^5}" for i in range(10)])
                    spectrum_slot.code(f"{p_str}\n{n_str}\n{pct_str}")
                    
                    sc_df = pd.DataFrame([
                        {"Market Asset": k, "Signal Intensity": f"{v:.1f}%"} 
                        for k, v in sorted(st.session_state.market_scores.items(), key=lambda item: item[1], reverse=True)
                    ])
                    screener_slot.dataframe(sc_df, use_container_width=True, hide_index=True, height=150)
                    
                    target_type = None
                    target_pred = None
                    is_sure_trade = False
                    
                    # --- CHITI CORE ALGORITHMIC CONFIRMATION RULES ---
                    if under_2 > 38.0 and digit in [0, 1]:
                        target_type, target_pred, is_sure_trade = "DIGITUNDER", 2, True
                    elif under_3 > 46.0 and digit in [0, 1, 2]:
                        target_type, target_pred, is_sure_trade = "DIGITUNDER", 3, True
                    elif over_8 > 22.0 and digit == 9:
                        target_type, target_pred, is_sure_trade = "DIGITOVER", 8, True
                    elif over_7 > 38.0 and digit in [8, 9]:
                        target_type, target_pred, is_sure_trade = "DIGITOVER", 7, True
                    elif under_8 > 66.0 and digit in [5, 6, 7]:
                        target_type, target_pred, is_sure_trade = "DIGITUNDER", 8, False
                    elif over_2 > 66.0 and digit in [2, 3, 4]:
                        target_type, target_pred, is_sure_trade = "DIGITOVER", 2, False

                    # Dispatch Automated Contract Placement Orders
                    if target_type is not None:
                        calc_stake = st.session_state.tracked_balance * (risk_percentage / 100.0)
                        base_stake = max(min_stake, round(calc_stake, 2))
                        
                        if is_sure_trade:
                            base_stake = round(base_stake * 1.5, 2)
                            st.session_state.current_action = f"🎯 SURE MATCH DETECTED! Compounding Stake Size to ${base_stake}"
                        else:
                            st.session_state.current_action = f"⚡ FREQUENCY SCALPER PLACED: Position Stake at ${base_stake}"
                            
                        console_slot.info(f"**🤖 ACTIVE CONSOLE LOG:** {st.session_state.current_action}")
                        
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
                            trades_slot.metric("Total Executions", st.session_state.total_trades)
                            ledger_slot.dataframe(pd.DataFrame(st.session_state.history).head(8), use_container_width=True, hide_index=True)
                            await asyncio.sleep(1.2) # Rapid reset delay to secure max contract frequency

    # Continuous loop executor loop block
    if st.session_state.running:
        asyncio.run(async_worker())

# Execute the core engine surface rendering pipeline loop natively
render_and_execute_engine()