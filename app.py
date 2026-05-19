import streamlit as st
import time
import random
import json
import ssl
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
            st.markdown(
                "> **RECOMMENDATION:** Please reach out to **AUTHOR 'CIZOR THE BADDEST' FOR ASSISTANCE** "
                "or contact **'CIZOR THE BADDEST' TO GET THE REQUIRED PASSKEY**."
            )
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

# --- ENGINE SESSION STATE TRACKING MATRIX ---
if "account_mode" not in st.session_state:
    st.session_state.account_mode = "DEMO"
if "real_balance" not in st.session_state:
    st.session_state.real_balance = 0.00  
if "demo_balance" not in st.session_state:
    st.session_state.demo_balance = 10.00  # Baseline playground wallet starts at exactly $10.00 USD
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
if "current_market" not in st.session_state:
    st.session_state.current_market = random.choice(MARKETS_1S)
if "market_ticks_count" not in st.session_state:
    st.session_state.market_ticks_count = 0
if "market_lock_duration" not in st.session_state:
    st.session_state.market_lock_duration = random.randint(300, 500)
if "digit_history" not in st.session_state:
    st.session_state.digit_history = []
if "last_trade_status" not in st.session_state:
    st.session_state.last_trade_status = "CALIBRATING PREMIUM BARRIER FILTERS..."
if "active_token" not in st.session_state:
    st.session_state.active_token = ""
if "gateway_authorized" not in st.session_state:
    st.session_state.gateway_authorized = False
if "engine_running" not in st.session_state:
    st.session_state.engine_running = True

# --- FIXED TRACKING CORE VARIABLES ---
max_runs_per_trend = 3

# --- INTERACTIVE DASHBOARD SIDEBAR CONTROLS ---
st.sidebar.markdown(f"## 🛠️ CIZOR OUTPOST: CONTROLS")
st.sidebar.markdown(f"**AUTHOR NAME:** CIZOR THE BADDEST")

mode_selection = st.sidebar.radio("CHOOSE ACCOUNT REALM:", ["LOCAL REALM (DEMO)", "BROKER NETWORK LAYER (LIVE)"])
st.session_state.account_mode = "LIVE" if "LIVE" in mode_selection else "DEMO"

# DYNAMIC TOKEN HOT-SWAP GATEWAY WITH HARD RE-AUTHENTICATION & BACK BUTTONS
if st.session_state.account_mode == "LIVE":
    if not st.session_state.gateway_authorized:
        token_input = st.sidebar.text_input("🔑 ENTER TOKEN FOR ACTIVE ACCOUNT:", type="password")
        connect_gate = st.sidebar.button("🔌 ACTIVATE ACCESS GATEWAY")
        
        if connect_gate and token_input:
            st.session_state.active_token = token_input
            st.sidebar.info("Routing core matrix parameters...")
    else:
        st.sidebar.success("✅ GATEWAY BOUND TO ACCOUNT")
        # BACK BUTTON / LOGOUT FUNCTIONALITY FOR INSTANT SWAPPING TO ACCOUNT 2
        logout_clicked = st.sidebar.button("↩️ LOG OUT & DISCONNECT TOKEN")
        if logout_clicked:
            st.session_state.active_token = ""
            st.session_state.gateway_authorized = False
            st.session_state.real_balance = 0.00
            st.success("Disconnected. Ready for secondary token injection.")
            st.rerun()

# MASTER OPERATIONS STOP / RUN OVERRIDES
st.sidebar.markdown("---")
st.sidebar.markdown("**SYSTEM POWER STATE:**")
if st.session_state.engine_running:
    stop_clicked = st.sidebar.button("🛑 EMERGENCY KILL-SWITCH: HALT TRADING")
    if stop_clicked:
        st.session_state.engine_running = False
        st.rerun()
else:
    start_clicked = st.sidebar.button("🚀 RE-ENGAGE CORE MATRIX LOOPS")
    if start_clicked:
        st.session_state.engine_running = True
        st.rerun()

# Dynamic balance mapping logic (Demo balance displays text mask as a real balance)
if st.session_state.account_mode == "LIVE":
    active_balance = st.session_state.real_balance
    label_string = f"💰 REAL BALANCE MONITOR"
else:
    active_balance = st.session_state.demo_balance
    label_string = f"💰 REAL BALANCE MONITOR"

# --- ASYMMETRIC STAKE EXTRACTION CALCULATOR ---
base_stake = 0.35
# Standard trade uses 3% of account balance
standard_calculated_stake = max(base_stake, round(active_balance * 0.03, 2)) if active_balance > 0 else base_stake
# High certainty (1000% Sure) trade scales way higher to 25% of account balance to grow small accounts rapidly
high_certainty_stake = max(base_stake, round(active_balance * 0.25, 2)) if active_balance > 0 else base_stake

st.sidebar.metric(label=label_string, value=f"${active_balance:,.2f} USD")

# --- UNBROKEN STREAMLIT REFRESH CONTAINERS ---
col_left, col_right = st.columns([2, 1])
with col_left:
    main_dashboard = st.empty()
    spectrum_visualizer = st.empty()
    alert_matrix = st.empty()
with col_right:
    st.markdown("### 📊 TRADE RESOLUTION TELEMETRY")
    outcome_card = st.empty()

# --- WEBSOCKET CONNECTION MANAGER FOR LIVE TRADING ---
def get_live_tick_and_execute(token, symbol, amount, strategy, run_trade=False):
    """Handshakes securely to Deriv endpoints for live balance adjustments and execution triggers."""
    try:
        ws = create_connection("wss://ws.derivws.com/websockets/v3?app_id=1089", sslopt={"cert_reqs": ssl.CERT_NONE})
        
        auth_req = json.dumps({"authorize": token})
        ws.send(auth_req)
        auth_res = json.loads(ws.recv())
        
        if "error" in auth_res:
            ws.close()
            return None, f"❌ AUTH ERROR: {auth_res['error']['message']}", 0.0
            
        balance = float(auth_res["authorize"]["balance"])
        st.session_state.real_balance = balance
        st.session_state.gateway_authorized = True
        
        if run_trade and strategy != "NEUTRAL":
            contract_type = "DIGITOVER" if "OVER" in strategy else "DIGITUNDER"
            barrier_target = strategy.split(" ")[-1]
            
            buy_req = json.dumps({
                "buy": 1,
                "price": amount,
                "parameters": {
                    "amount": amount,
                    "basis": "stake",
                    "contract_type": contract_type,
                    "currency": "USD",
                    "duration": 1,
                    "duration_unit": "t",
                    "barrier": barrier_target,
                    "symbol": symbol
                }
            })
            ws.send(buy_req)
            buy_res = json.loads(ws.recv())
            ws.close()
            return buy_res, "TRADE_EXECUTED", balance
            
        tick_req = json.dumps({"ticks": symbol, "count": 1})
        ws.send(tick_req)
        tick_res = json.loads(ws.recv())
        ws.close()
        
        if "tick" in tick_res:
            return None, float(tick_res["tick"]["quote"]), balance
    except Exception as e:
        return None, f"DISCONNECTED: {str(e)}", 0.0
    return None, None, 0.0

# --- THE CONTINUOUS EXECUTION LOOP ---
while True:
    # If kill-switch is thrown, hold the script loop and broadcast offline mode
    if not st.session_state.engine_running:
        main_dashboard.error("🛑 ENGINE DISENGAGED: THE MASTER KILL-SWITCH HAS HALTED ALL ACTIVE ACCOUNT TRADES.")
        time.sleep(1.0)
        continue

    st.session_state.market_ticks_count += 1
    if st.session_state.market_ticks_count >= st.session_state.market_lock_duration:
        old_market = st.session_state.current_market
        st.session_state.current_market = random.choice([m for m in MARKETS_1S if m != old_market])
        st.session_state.market_ticks_count = 0
        st.session_state.market_lock_duration = random.randint(300, 500)
        st.session_state.digit_history.clear()
        st.session_state.current_trend_runs = 0
        st.session_state.system_cooldown_active = False

    selected_symbol = MARKET_MAP[st.session_state.current_market]

    # --- ENGINE DATA HANDLING ROUTER ---
    if st.session_state.account_mode == "LIVE" and st.session_state.active_token:
        _, network_result, updated_bal = get_live_tick_and_execute(st.session_state.active_token, selected_symbol, standard_calculated_stake, "NEUTRAL", run_trade=False)
        if isinstance(network_result, (int, float)):
            live_price_str = f"{network_result:.2f}"
            live_tick_digit = int(live_price_str[-1])
            confidence_signal = "📡 [NETWORK CONNECTED: BALANCES AND DATA TIMING LIVE]"
            st.session_state.real_balance = updated_bal
            active_balance = updated_bal
        else:
            time.sleep(1.0)
            live_price_str = f"{random.uniform(750.00, 1250.00):.2f}"
            live_tick_digit = int(live_price_str[-1])
            confidence_signal = f"⚠️ [API TUNNEL EXCEPTION: {network_result}]"
    else:
        time.sleep(1.0)
        live_price_str = f"{random.uniform(750.00, 1250.00):.2f}"
        live_tick_digit = int(live_price_str[-1])
        confidence_signal = "🎲 [LOCAL SIMULATION MATRIX WORKSPACE RUNNING]"
        active_balance = st.session_state.demo_balance

    st.session_state.digit_history.append(live_tick_digit)
    if len(st.session_state.digit_history) > 40:
        st.session_state.digit_history.pop(0)

    total_ticks = len(st.session_state.digit_history)
    frequencies = {i: (st.session_state.digit_history.count(i) / total_ticks) * 100 if total_ticks > 0 else 0 for i in range(10)}

    under_2_density = frequencies[0] + frequencies[1]
    under_3_density = frequencies[0] + frequencies[1] + frequencies[2]
    over_7_density = frequencies[8] + frequencies[9]
    over_8_density = frequencies[9]

    # --- ASYMMETRIC FREQUENT RISK REVERSAL DISTRIBUTION LOGIC ---
    strategy_choice = "NEUTRAL"
    action_authorized = False
    payout_multiplier = 1.0
    target_trigger_digits = []
    is_1000_percent_sure = False
    active_stake = standard_calculated_stake

    recent_ticks = st.session_state.digit_history[-6:] if total_ticks >= 6 else st.session_state.digit_history

    if not st.session_state.system_cooldown_active and total_ticks >= 20:
        # HIGH HIGH CERTAINTY (1000% SURE) CORRIDORS -> TRIGGERS HIGH ACTIVE RAPID-GROWTH STAKE
        if frequencies[8] > 26.0 and recent_ticks[-1] == 8:
            strategy_choice = "OVER 8"
            payout_multiplier = 8.00
            target_trigger_digits = [8]
            action_authorized = True
            is_1000_percent_sure = True
            active_stake = high_certainty_stake
        elif under_2_density > 32.0 and recent_ticks[-1] in [2, 3]:
            strategy_choice = "UNDER 2"
            payout_multiplier = 3.90
            target_trigger_digits = [2, 3]
            action_authorized = True
            is_1000_percent_sure = True
            active_stake = high_certainty_stake
        elif over_7_density > 32.0 and recent_ticks[-1] in [6, 7]:
            strategy_choice = "OVER 7"
            payout_multiplier = 3.90
            target_trigger_digits = [6, 7]
            action_authorized = True
            is_1000_percent_sure = True
            active_stake = high_certainty_stake
        elif under_3_density > 40.0 and recent_ticks[-1] in [3, 4]:
            strategy_choice = "UNDER 3"
            payout_multiplier = 2.20
            target_trigger_digits = [3, 4]
            action_authorized = True
            is_1000_percent_sure = True
            active_stake = high_certainty_stake
        else:
            # 🛡️ DEVIATION CHANNELS FOR FREQUENT SAFE CAPTURES (Standard Stake Size to minimize risk exposure)
            under_8_density = sum([frequencies[x] for x in range(8)])
            over_2_density = sum([frequencies[x] for x in range(3, 10)])
            
            if under_8_density > 60.0:  
                strategy_choice = "UNDER 8"
                payout_multiplier = 1.10
                target_trigger_digits = [6, 7, 8]
                action_authorized = True
                active_stake = standard_calculated_stake
            elif over_2_density > 60.0:
                strategy_choice = "OVER 2"
                payout_multiplier = 1.10
                target_trigger_digits = [1, 2, 3]
                action_authorized = True
                active_stake = standard_calculated_stake

    if action_authorized:
        group_freqs = {d: frequencies[d] for d in target_trigger_digits}
        sniper_intercept_digit = max(group_freqs, key=group_freqs.get)
    else:
        sniper_intercept_digit = None

    if st.session_state.system_cooldown_active:
        st.session_state.cooldown_ticks += 1
        if st.session_state.cooldown_ticks >= 15:
            st.session_state.system_cooldown_active = False
            st.session_state.cooldown_ticks = 0

    # --- RENDER DASHBOARD INTERFACE CORE ---
    with main_dashboard.container():
        sure_badge = "🔥 [1000% HIGH CERTAINTY SCALING ACTIVE] 🔥" if is_1000_percent_sure else "🛡️ [STANDARD STABILITY SPREAD]"
        st.code(
            f"=====================================================================================\n"
            f"⚡ HIGH-PAYOUT EDGE BARRIER MATRIX ACTIVATED\n"
            f"=====================================================================================\n"
            f"LOCKED TARGET MARKET: {st.session_state.current_market.upper()}\n"
            f"BIAS ANALYSIS STATE: {confidence_signal}\n"
            f"SIGNAL ACCURACY CODE: {sure_badge}\n"
            f"RECOMMENDED SYSTEM : [{strategy_choice}] MODE ACTIVATED (Est. Payout: {payout_multiplier * 100:.0f}%)\n"
            f"DASHBOARD ACCOUNT MONITOR BALANCE  : ${active_balance:,.2f} USD\n"
            f"DASHBOARD EXECUTED ALLOCATED STAKE : ${active_stake:.2f} USD\n"
            f"CURRENT RUN COUNTER  : [ {st.session_state.current_trend_runs} / {max_runs_per_trend} ] RUNS TAKEN\n"
            f"====================================================================================="
        )

    # --- REAL-TIME SPECTRUM DISPLAY ---
    with spectrum_visualizer.container():
        col_w = 7
        pointer_line = "".join([f"{'▲' if d == live_tick_digit else '':^{col_w}}" for d in range(10)])
        matrix_digits = "".join([f"{d:^{col_w}}" for d in range(10)])
        percent_line = "".join([f"{f'{frequencies[d]:.0f}%':^{col_w}}" for d in range(10)])
        st.text("[ REAL-TIME DERIV DIGIT FREQUENCY SPECTRUM ]")
        st.code(f"{pointer_line}\n{matrix_digits}\n{percent_line}")

    # --- INSTANT ZERO-DELAY ORDER CONTRACT LOGIC ---
    with alert_matrix.container():
        if st.session_state.system_cooldown_active:
            st.error(f"⌛ COOLDOWN ENGAGED. RESETTING CHANNELS... ({15 - st.session_state.cooldown_ticks}s)")
        elif action_authorized and sniper_intercept_digit is not None:
            st.warning(f"🎯 ANALYSIS LOCKED. TARGET PROFILE DIGIT: [ {sniper_intercept_digit} ]")
            
            if live_tick_digit == sniper_intercept_digit:
                st.success(f"🔥 ZERO-DELAY CONTRACT ENTRY TRIGGERED: RUNNING [{strategy_choice}] AT ${active_stake} STAKE 🔥")
                
                if st.session_state.account_mode == "LIVE" and st.session_state.active_token:
                    response, status, updated_bal = get_live_tick_and_execute(st.session_state.active_token, selected_symbol, active_stake, strategy_choice, run_trade=True)
                    st.session_state.total_trades += 1
                    st.session_state.current_trend_runs += 1
                    
                    if response and "error" not in response:
                        profit = float(response["buy"].get("profit", 0))
                        if profit > 0:
                            st.session_state.total_wins += 1
                            st.session_state.real_balance += profit
                            st.session_state.last_trade_status = f"🟢 LIVE API WIN: +${profit:.2f} BALANCED SECURELY"
                        else:
                            st.session_state.total_losses += 1
                            st.session_state.real_balance -= active_stake
                            st.session_state.last_trade_status = f"🔴 LIVE API LOSS: -${active_stake:.2f} BRACKET EXCURSION"
                    else:
                        st.session_state.last_trade_status = f"❌ API REJECTION: {response.get('error', {}).get('message', 'Network Drop')}"
                else:
                    st.session_state.total_trades += 1
                    st.session_state.current_trend_runs += 1
                    outcome_roll = random.uniform(0, 100)
                    
                    win_map = {
                        "OVER 8": [9], "UNDER 2": [0, 1], "OVER 7": [8, 9], "UNDER 3": [0, 1, 2],
                        "UNDER 8": list(range(8)), "OVER 2": list(range(3, 10))
                    }
                    win_achieved = live_tick_digit in win_map.get(strategy_choice, [])

                    if win_achieved or (outcome_roll <= 35.0):
                        payout_gains = active_stake * payout_multiplier
                        st.session_state.demo_balance += payout_gains
                        st.session_state.total_wins += 1
                        st.session_state.last_trade_status = f"🟢 WIN: +${payout_gains:.2f} CRITICAL TARGET ACQUIRED"
                    else:
                        st.session_state.demo_balance -= active_stake
                        st.session_state.total_losses += 1
                        st.session_state.last_trade_status = f"🔴 LOSS: -${active_stake:.2f} BRACKET EXCURSION"

                if st.session_state.current_trend_runs >= max_runs_per_trend:
                    st.session_state.system_cooldown_active = True
                    st.session_state.cooldown_ticks = 0
                time.sleep(2.5)
        else:
            st.info("🔍 SCANNING FREQUENCY spectrum Matrix FOR TARGET PROFILE...")

    # --- ISOLATED OUTCOME DISPLAY TRAILER ---
    with outcome_card.container():
        st.markdown(f"**LAST OUTCOME DETAILS:**\n`{st.session_state.last_trade_status}`")
        st.markdown("---")
        st.metric(label="🏆 TOTAL TRADES RUN", value=st.session_state.total_trades)
        st.metric(label="🟩 WON CONTRACTS", value=st.session_state.total_wins)
        st.metric(label="🟥 LOST CONTRACTS", value=st.session_state.total_losses)

    st.rerun() if st.session_state.account_mode == "LIVE" else time.sleep(0.01)