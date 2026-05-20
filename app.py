import streamlit as st
import time
import random
import json
import ssl
from websocket import create_connection

# --- PRIVATE LOCAL CONTAINER LAYER ---
st.set_page_config(page_title="Chiti Core Engine", page_icon="⚡", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 CIZOR INTERCEPT GATEWAY")
    input_passkey = st.text_input("ENTER OPERATIONAL PASSKEY:", type="password")
    if st.button("🚀 RELEASE ENGINE"):
        if input_passkey == "2PRK9HH#":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ INVALID.")
    st.stop()

# --- LOCAL MATRIX MAP ---
MARKET_MAP = {
    "Volatility 10 (1s) Index": "1HZ10V",
    "Volatility 25 (1s) Index": "1HZ25V",
    "Volatility 50 (1s) Index": "1HZ50V",
    "Volatility 75 (1s) Index": "1HZ75V",
    "Volatility 100 (1s) Index": "1HZ100V"
}
MARKETS_1S = list(MARKET_MAP.keys())

# --- INSTANCE DATA ---
if "tracked_balance" not in st.session_state: st.session_state.tracked_balance = 10.00  
if "digit_history" not in st.session_state: st.session_state.digit_history = []
if "current_market" not in st.session_state: st.session_state.current_market = random.choice(MARKETS_1S)
if "market_ticks_count" not in st.session_state: st.session_state.market_ticks_count = 0
if "market_lock_duration" not in st.session_state: st.session_state.market_lock_duration = random.randint(300, 500)
if "active_token" not in st.session_state: st.session_state.active_token = ""
if "gateway_authorized" not in st.session_state: st.session_state.gateway_authorized = False

# --- CONTROLS OUTPOST ---
st.sidebar.markdown("### 🛠️ CHITI CORE CONTROLS")
if not st.session_state.gateway_authorized:
    token_input = st.sidebar.text_input("🔑 API TOKEN:", type="password")
    if st.sidebar.button("🔌 CONNECT"):
        st.session_state.active_token = token_input
        st.session_state.gateway_authorized = True
        st.rerun()
else:
    if st.sidebar.button("↩️ DISCONNECT"):
        st.session_state.active_token = ""
        st.session_state.gateway_authorized = False
        st.rerun()

st.sidebar.metric(label="💰 BALANCE", value=f"${st.session_state.tracked_balance:,.2f}")

main_dashboard = st.empty()
spectrum_visualizer = st.empty()

def fetch_live_market_tick(token, symbol):
    try:
        ws = create_connection("wss://ws.derivws.com/websockets/v3?app_id=1089", sslopt={"cert_reqs": ssl.CERT_NONE}, timeout=2)
        if token:
            ws.send(json.dumps({"authorize": token}))
            auth_res = json.loads(ws.recv())
            if "authorize" in auth_res:
                st.session_state.tracked_balance = float(auth_res["authorize"]["balance"])
        ws.send(json.dumps({"ticks": symbol, "count": 1}))
        tick_res = json.loads(ws.recv())
        ws.close()
        if "tick" in tick_res:
            return float(tick_res["tick"]["quote"])
    except:
        return None
    return None

st.session_state.market_ticks_count += 1
if st.session_state.market_ticks_count >= st.session_state.market_lock_duration:
    old_m = st.session_state.current_market
    st.session_state.current_market = random.choice([m for m in MARKETS_1S if m != old_m])
    st.session_state.market_ticks_count = 0
    st.session_state.market_lock_duration = random.randint(300, 500)
    st.session_state.digit_history.clear()

selected_symbol = MARKET_MAP[st.session_state.current_market]
result_data = fetch_live_market_tick(st.session_state.active_token, selected_symbol)

if result_data:
    live_tick_digit = int(f"{result_data:.2f}"[-1])
else:
    time.sleep(0.4)
    live_tick_digit = random.randint(0, 9)

st.session_state.digit_history.append(live_tick_digit)
if len(st.session_state.digit_history) > 40:
    st.session_state.digit_history.pop(0)

total_ticks = len(st.session_state.digit_history)
frequencies = {i: (st.session_state.digit_history.count(i) / total_ticks) * 100 if total_ticks > 0 else 0 for i in range(10)}

with main_dashboard.container():
    st.code(
        f"===================================================================\n"
        f"⚡ CHITI LIVE PROCESSING UNIT\n"
        f"===================================================================\n"
        f"CURRENT RUNNING MARKET : {st.session_state.current_market.upper()}\n"
        f"SYNCHRONIZED BALANCE   : ${st.session_state.tracked_balance:,.2f} USD\n"
        f"==================================================================="
    )

with spectrum_visualizer.container():
    col_w = 6
    pointer_line = "".join([f"{'▲' if d == live_tick_digit else '':^{col_w}}" for d in range(10)])
    matrix_digits = "".join([f"{d:^{col_w}}" for d in range(10)])
    percent_line = "".join([f"{f'{frequencies[d]:.0f}%':^{col_w}}" for d in range(10)])
    st.code(f"{pointer_line}\n{matrix_digits}\n{percent_line}")

time.sleep(0.6)
st.rerun()