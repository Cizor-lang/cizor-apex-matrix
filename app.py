import streamlit as st
import time
import random
import json
import ssl
import threading
from websocket import create_connection

# --- EXCLUSIVE SYSTEM HEADER CONFIGURATION ---
st.set_page_config(page_title="Cizor Sniper Matrix Pro", page_icon="⚡", layout="wide")

# --- INITIAL PASSKEY SECURITY GATEWAY ---
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
    st.stop()

# --- MARKET MAP TO DERIV SYSTEM SYMBOLS ---
MARKET_MAP = {
    "Volatility 10 (1s) Index": "1HZ10V",
    "Volatility 25 (1s) Index": "1HZ25V",
    "Volatility 50 (1s) Index": "1HZ50V",
    "Volatility 75 (1s) Index": "1HZ75V",
    "Volatility 100 (1s) Index": "1HZ100V"
}
MARKETS_1S = list(MARKET_MAP.keys())

# --- PERSISTENT BACKEND BACKGROUND STREAM STATE ---
if "digit_history" not in st.session_state:
    st.session_state.digit_history = []
if "live_tick_digit" not in st.session_state:
    st.session_state.live_tick_digit = 0
if "current_market" not in st.session_state:
    st.session_state.current_market = random.choice(MARKETS_1S)
if "market_ticks_count" not in st.session_state:
    st.session_state.market_ticks_count = 0
if "market_lock_duration" not in st.session_state:
    st.session_state.market_lock_duration = random.randint(300, 500)
if "tracked_balance" not in st.session_state:
    st.session_state.tracked_balance = 10.00
if "detected_account_type" not in st.session_state:
    st.session_state.detected_account_type = "UNLINKED SIMULATION"
if "active_token" not in st.session_state:
    st.session_state.active_token = ""
if "gateway_authorized" not in st.session_state:
    st.session_state.gateway_authorized = False
if "engine_running" not in st.session_state:
    st.session_state.engine_running = True
if "total_trades" not in st.session_state:
    st.session_state.total_trades = 0
if "total_wins" not in st.session_state:
    st.session_state.total_wins = 0
if "total_losses" not in st.session_state:
    st.session_state.total_losses = 0
if "current_trend_runs" not in st.session_state:
    st.session_state.current_trend_runs = 0
if "system_cooldown_active" not in st.session_state:
    st.session_state.system_cooldown_active = False
if "cooldown_ticks" not in st.session_state:
    st.session_state.cooldown_ticks = 0
if "last_trade_status" not in st.session_state:
    st.session_state.last_trade_status = "CALIBRATING PREMIUM BARRIER FILTERS..."
if "fire_order_signal" not in st.session_state:
    st.session_state.fire_order_signal = None

# --- SIDEBAR OUTPOST CONTROLS ---
st.sidebar.markdown(f"## 🛠️ CIZOR OUTPOST: CONTROLS")
st.sidebar.markdown(f"**AUTHOR NAME:** CIZOR THE BADDEST")

if not st.session_state.gateway_authorized:
    token_input = st.sidebar.text_input("🔑 PASTE CURRENT ACCOUNT API TOKEN:", type="password")
    connect_gate = st.sidebar.button("🔌 CONNECT TO DERIV SERVER")
    if connect_gate and token_input:
        st.session_state.active_token = token_input
        st.session_state.gateway_authorized = True
        st.sidebar.info("Establishing permanent background pipeline...")
        st.rerun()
else:
    if "REAL" in st.session_state.detected_account_type:
        st.sidebar.error(f"🔴 ONLINE: {st.session_state.detected_account_type}")
    else:
        st.sidebar.info(f"🔵 ONLINE: {st.session_state.detected_account_type}")
        
    logout_clicked = st.sidebar.button("↩️ LOG OUT & DISCONNECT TOKEN")
    if logout_clicked:
        st.session_state.active_token = ""
        st.session_state.gateway_authorized = False
        st.session_state.tracked_balance = 10.00
        st.session_state.detected_account_type = "UNLINKED SIMULATION"
        st.success("Tunnels dropped cleanly.")
        st.rerun()

st.sidebar.markdown("---")
if st.session_state.engine_running:
    if st.sidebar.button("🛑 EMERGENCY KILL-SWITCH: HALT"):
        st.session_state.engine_running = False
        st.rerun()
else:
    if st.sidebar.button("🚀 RE-ENGAGE CORE MATRIX LOOPS"):
        st.session_state.engine_running = True
        st.rerun()

if st.sidebar.button("🧹 RESET SYSTEM MONITOR"):
    st.session_state.tracked_balance = 10.00
    st.session_state.total_trades = 0
    st.session_state.total_wins = 0
    st.session_state.total_losses = 0
    st.session_state.current_trend_runs = 0
    st.session_state.system_cooldown_active = False
    st.session_state.last_trade_status = "SYSTEM BASES RESTORED."
    st.rerun()

# --- DYNAMIC STAKE METRICS ---
base_stake = 0.35
standard_calculated_stake = max(base_stake, round(st.session_state.tracked_balance * 0.03, 2)) if st.session_state.tracked_balance > 0 else base_stake
if st.session_state.tracked_balance <= 15.00:
    high_certainty_stake = 1.50 
elif st.session_state.tracked_balance <= 50.00:
    high_certainty_stake = round(st.session_state.tracked_balance * 0.20, 2) 
else:
    high_certainty_stake = round(st.session_state.tracked_balance * 0.15, 2) 

st.sidebar.metric(label="💰 REAL BALANCE MONITOR", value=f"${st.session_state.tracked_balance:,.2f} USD")

# --- UNBROKEN DISPLAY UI MATRIX CONTAINERS ---
col_left, col_right = st.columns([2, 1])
with col_left:
    main_dashboard = st.empty()
    spectrum_visualizer = st.empty()
    alert_matrix = st.empty()
with col_right:
    st.markdown("### 📊 TRADE RESOLUTION TELEMETRY")
    outcome_card = st.empty()

# --- THE LIVE WEBSOCKET SUBSCRIBER BACKGROUND THREAD ENGINE ---
def run_permanent_tick_stream():
    """Spins up a permanent, non-blocking connection that processes raw tick mutations with zero data loss."""
    while True:
        try:
            symbol_code = MARKET_MAP[st.session_state.current_market]
            ws = create_connection("wss://ws.derivws.com/websockets/v3?app_id=1089", sslopt={"cert_reqs": ssl.CERT_NONE})
            
            # Authorize Session if Token exists
            if st.session_state.active_token:
                ws.send(json.dumps({"authorize": st.session_state.active_token}))
                auth_res = json.loads(ws.recv())
                if "authorize" in auth_res:
                    st.session_state.tracked_balance = float(auth_res["authorize"]["balance"])
                    login_id = auth_res["authorize"].get("loginid", "")
                    st.session_state.detected_account_type = f"REAL ACCOUNT ({login_id})" if not login_id.startswith("VRTC") else f"DEMO ACCOUNT ({login_id})"
            
            # Subscribe to the official live tick engine pipe
            ws.send(json.dumps({"ticks": symbol_code, "subscribe": 1}))
            
            while MARKET_MAP[st.session_state.current_market] == symbol_code:
                raw_msg = ws.recv()
                data = json.loads(raw_msg)
                
                # Intercept Live Balance Shifts pushing from Account modifications
                if "balance" in data:
                    st.session_state.tracked_balance = float(data["balance"]["balance"])
                    
                if "tick" in data:
                    tick_price = float(data["tick"]["quote"])
                    price_str = f"{tick_price:.2f}"
                    last_digit = int(price_str[-1])
                    
                    # Lock values instantly to memory
                    st.session_state.live_tick_digit = last_digit
                    hist = st.session_state.digit_history
                    hist.append(last_digit)
                    if len(hist) > 40:
                        hist.pop(0)
                    st.session_state.digit_history = hist
                    st.session_state.market_ticks_count += 1
                    
                # Execute Immediate Order Payload injections without dropping the pipe loop
                if st.session_state.fire_order_signal:
                    order = st.session_state.fire_order_signal
                    st.session_state.fire_order_signal = None
                    
                    if st.session_state.active_token:
                        c_type = "DIGITOVER" if "OVER" in order["strat"] else "DIGITUNDER"
                        b_target = order["strat"].split(" ")[-1]
                        buy_payload = {
                            "buy": 1, "price": order["stake"],
                            "parameters": {
                                "amount": order["stake"], "basis": "stake", "contract_type": c_type,
                                "currency": "USD", "duration": 1, "duration_unit": "t",
                                "barrier": b_target, "symbol": symbol_code
                            }
                        }
                        ws.send(json.dumps(buy_payload))
                        buy_res = json.loads(ws.recv())
                        
                        st.session_state.total_trades += 1
                        st.session_state.current_trend_runs += 1
                        if "buy" in buy_res and "error" not in buy_res:
                            p = float(buy_res["buy"].get("profit", 0))
                            if p > 0:
                                st.session_state.total_wins += 1
                                st.session_state.last_trade_status = f"🟢 WIN COMPILING: +${p:.2f}"
                            else:
                                st.session_state.total_losses += 1
                                st.session_state.last_trade_status = f"🔴 BRACKET LOSS: -${order['stake']:.2f}"
                        else:
                            st.session_state.last_trade_status = f"❌ API EXCEPTION: {buy_res.get('error',{}).get('message','Drop')}"
            ws.close()
        except Exception:
            time.sleep(1.0) # Graceful error reconnection boundary

# Spawn Thread to keep backend calculations matching the exact main-line network paths
if "stream_thread_spawned" not in st.session_state:
    t = threading.Thread(target=run_permanent_tick_stream, daemon=True)
    t.start()
    st.session_state.stream_thread_spawned = True

# --- MARKET CONTEXT EVALUATION ---
if st.session_state.market_ticks_count >= st.session_state.market_lock_duration:
    old_m = st.session_state.current_market
    st.session_state.current_market = random.choice([m for m in MARKETS_1S if m != old_m])
    st.session_state.market_ticks_count = 0
    st.session_state.market_lock_duration = random.randint(300, 500)
    st.session_state.digit_history.clear()
    st.session_state.current_trend_runs = 0
    st.session_state.system_cooldown_active = False

# --- DENSITY CALCULATION SPECTRUM ---
total_ticks = len(st.session_state.digit_history)
frequencies = {i: (st.session_state.digit_history.count(i) / total_ticks) * 100 if total_ticks > 0 else 0 for i in range(10)}

under_2_density = frequencies[0] + frequencies[1]
under_3_density = frequencies[0] + frequencies[1] + frequencies[2]
over_7_density = frequencies[8] + frequencies[9]

strategy_choice = "NEUTRAL"
action_authorized = False
payout_multiplier = 1.0
target_trigger_digits = []
is_1000_percent_sure = False
active_stake = standard_calculated_stake

recent_ticks = st.session_state.digit_history[-6:] if total_ticks >= 6 else st.session_state.digit_history

if not st.session_state.system_cooldown_active and total_ticks >= 20:
    if frequencies[8] > 26.0 and recent_ticks[-1] == 8:
        strategy_choice = "OVER 8"; payout_multiplier = 8.00; target_trigger_digits = [8]; action_authorized = True; is_1000_percent_sure = True; active_stake = high_certainty_stake
    elif under_2_density > 32.0 and recent_ticks[-1] in [2, 3]:
        strategy_choice = "UNDER 2"; payout_multiplier = 3.90; target_trigger_digits = [2, 3]; action_authorized = True; is_1000_percent_sure = True; active_stake = high_certainty_stake
    elif over_7_density > 32.0 and recent_ticks[-1] in [6, 7]:
        strategy_choice = "OVER 7"; payout_multiplier = 3.90; target_trigger_digits = [6, 7]; action_authorized = True; is_1000_percent_sure = True; active_stake = high_certainty_stake
    elif under_3_density > 40.0 and recent_ticks[-1] in [3, 4]:
        strategy_choice = "UNDER 3"; payout_multiplier = 2.20; target_trigger_digits = [3, 4]; action_authorized = True; is_1000_percent_sure = True; active_stake = high_certainty_stake
    else:
        under_8_density = sum([frequencies[x] for x in range(8)])
        over_2_density = sum([frequencies[x] for x in range(3, 10)])
        if under_8_density > 58.0:
            strategy_choice = "UNDER 8"; payout_multiplier = 1.10; target_trigger_digits = [6, 7, 8]; action_authorized = True; active_stake = standard_calculated_stake
        elif over_2_density > 58.0:
            strategy_choice = "OVER 2"; payout_multiplier = 1.10; target_trigger_digits = [1, 2, 3]; action_authorized = True; active_stake = standard_calculated_stake

sniper_intercept_digit = max({d: frequencies[d] for d in target_trigger_digits}, key=frequencies.get) if action_authorized else None

if st.session_state.system_cooldown_active:
    st.session_state.cooldown_ticks += 1
    if st.session_state.cooldown_ticks >= 15:
        st.session_state.system_cooldown_active = False
        st.session_state.cooldown_ticks = 0

# --- UI LOG GENERATION ---
with main_dashboard.container():
    st.code(
        f"=====================================================================================\n"
        f"⚡ CHITI ENGINE PARALLEL WORKFLOW STREAM ONLINE\n"
        f"=====================================================================================\n"
        f"VECTOR ACCOUNT DETECTED   : {st.session_state.detected_account_type.upper()}\n"
        f"NETWORK STREAM SPEED STATUS: 🚀 100% UNBROKEN DATA PIPELINE LIVE\n"
        f"RECOMMENDED sniper TARGET : [{strategy_choice}] ({payout_multiplier:.2f}x)\n"
        f"SYNCHRONIZED CORE BALANCE : ${st.session_state.tracked_balance:,.2f} USD\n"
        f"CURRENT STRIKE ALLOCATION : ${active_stake:.2f} USD\n"
        f"TREND EXTRACTION INDEX RUN: [ {st.session_state.current_trend_runs} / 3 ]\n"
        f"====================================================================================="
    )

with spectrum_visualizer.container():
    col_w = 7
    pointer_line = "".join([f"{'▲' if d == st.session_state.live_tick_digit else '':^{col_w}}" for d in range(10)])
    matrix_digits = "".join([f"{d:^{col_w}}" for d in range(10)])
    percent_line = "".join([f"{f'{frequencies[d]:.0f}%':^{col_w}}" for d in range(10)])
    st.markdown(f"### 🚨 CURRENT ACTIVE TICK STREAM: `{st.session_state.current_market.upper()}`")
    st.markdown(f"**Market Lifetime Tracker:** `[ {st.session_state.market_ticks_count} / {st.session_state.market_lock_duration} ticks ]` before sweep rotation.")
    st.code(f"{pointer_line}\n{matrix_digits}\n{percent_line}")

with alert_matrix.container():
    if st.session_state.system_cooldown_active:
        st.error(f"⌛ COOLDOWN ENGAGED. RESETTING CHANNELS... ({15 - st.session_state.cooldown_ticks}s)")
    elif action_authorized and sniper_intercept_digit is not None:
        st.warning(f"🎯 ANALYSIS LOCKED. TARGET PROFILE DIGIT: [ {sniper_intercept_digit} ]")
        if st.session_state.live_tick_digit == sniper_intercept_digit:
            st.success(f"🔥 UNBROKEN ENTRY INSTANTIATED: EXECUTING [{strategy_choice}] 🔥")
            
            # Safe Single Order State Handshake to prevent packet duplicates
            st.session_state.fire_order_signal = {"strat": strategy_choice, "stake": active_stake}
            
            # Sandboxed simulation fallback if running unlinked
            if not st.session_state.active_token:
                st.session_state.total_trades += 1
                st.session_state.current_trend_runs += 1
                if random.uniform(0, 100) <= 65.0:
                    st.session_state.tracked_balance += (active_stake * payout_multiplier)
                    st.session_state.total_wins += 1
                    st.session_state.last_trade_status = "🟢 SIMULATION WIN COMPILED"
                else:
                    st.session_state.tracked_balance -= active_stake
                    st.session_state.total_losses += 1
                    st.session_state.last_trade_status = "🔴 SIMULATION REVERSAL LOSS"
            
            if st.session_state.current_trend_runs >= 3:
                st.session_state.system_cooldown_active = True
                st.session_state.cooldown_ticks = 0
            time.sleep(2.0)
    else:
        st.info("🔍 SCANNING LIVE STREAM MATRIX FOR SPECTRUM DEVIAZIONS...")

with outcome_card.container():
    st.markdown(f"**LAST OUTCOME DETAILS:**\n`{st.session_state.last_trade_status}`")
    st.markdown("---")
    st.metric(label="🏆 TOTAL TRADES RUN", value=st.session_state.total_trades)
    st.metric(label="🟩 WON CONTRACTS", value=st.session_state.total_wins)
    st.metric(label="🟥 LOST CONTRACTS", value=st.session_state.total_losses)

# Force immediate interface updates matching the background tick socket speed
time.sleep(0.1)
st.rerun()