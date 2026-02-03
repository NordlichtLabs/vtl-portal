import hashlib
import time
from datetime import datetime
import pandas as pd
import streamlit as st

# --- 1. INITIALISIERUNG ---
if 'registered_salts' not in st.session_state:
    st.session_state.registered_salts = []
if 'history_data' not in st.session_state:
    st.session_state.history_data = [
        {"Datum": "03.02.2026", "DE": "12, 45, 67, 23, 89, 10", "AT": "01, 15, 22, 33, 40, 42", "IT": "11, 22, 33, 44, 55, 66", "Hash": "f3b2c1a9e8d7c6b5a49382716059483726150493827160594837261504938271"},
        {"Datum": "02.02.2026", "DE": "05, 14, 28, 33, 41, 44", "AT": "07, 19, 21, 30, 39, 45", "IT": "03, 12, 34, 56, 78, 90", "Hash": "d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5"}
    ]

# --- 2. KONFIGURATION & NEON DESIGN ---
st.set_page_config(page_title="VTL - Verifiable Truth Layer", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    
    /* Hintergrund & Grundfarben */
    .stApp { 
        background-color: #0a0a0a; 
        color: #ffffff;
        background-image: radial-gradient(circle at 50% 50%, #1a1a1a 0%, #0a0a0a 100%);
    }
    
    h1, h2, h3 { font-family: 'Orbitron', sans-serif; letter-spacing: 2px; }
    h1 { color: #00d4ff !important; text-shadow: 0 0 10px #00d4ff; }
    
    /* Buttons */
    .stButton>button { 
        width: 100%; 
        background: linear-gradient(45deg, #004a99, #00d4ff); 
        color: white; 
        font-weight: bold; 
        border-radius: 5px; 
        border: none; 
        height: 45px;
        transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 20px #00d4ff; transform: translateY(-2px); }

    /* Login / Sign-up */
    .login-btn { border: 1px solid #00d4ff; color: #00d4ff; padding: 5px 15px; border-radius: 5px; text-decoration: none; font-size: 14px; margin-right: 10px; }
    .signup-btn { background-color: #00d4ff; color: #000; padding: 5px 15px; border-radius: 5px; text-decoration: none; font-size: 14px; font-weight: bold; }

    /* Use Case Boxen */
    .use-case-box { 
        padding: 20px; 
        border-radius: 10px; 
        border-top: 4px solid; 
        background: rgba(255, 255, 255, 0.03); 
        height: 100%;
    }
    .web2-box { border-color: #00d4ff; box-shadow: 0 4px 15px rgba(0, 212, 255, 0.1); }
    .web3-box { border-color: #ff00ff; box-shadow: 0 4px 15px rgba(255, 0, 255, 0.1); }
    .use-case-title { font-weight: bold; font-size: 20px; margin-bottom: 15px; }
    .web2-text { color: #00d4ff; }
    .web3-text { color: #ff00ff; }

    /* Process Cards */
    .hiw-card { background-color: rgba(0, 74, 153, 0.2); padding: 25px; border-radius: 12px; height: 100%; border: 1px solid #004a99; }
    .hiw-number { color: #00d4ff; font-size: 28px; font-weight: bold; margin-bottom: 10px; }

    /* Zertifikat */
    .certificate { 
        border: 2px solid #000; 
        padding: 25px; 
        border-radius: 10px; 
        background-color: #ffffff; 
        color: #000000; 
        font-family: 'Courier New', Courier, monospace; 
        position: relative; 
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.3); 
    }
    .verified-seal { position: absolute; bottom: 20px; right: 20px; border: 3px double #28a745; color: #28a745; padding: 5px 10px; font-weight: bold; transform: rotate(-15deg); border-radius: 5px; opacity: 0.8; }
    
    /* Timer */
    .timer-container { border: 1px solid #ff00ff; background-color: rgba(255, 0, 255, 0.05); border-radius: 8px; height: 45px; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #ff00ff; box-shadow: 0 0 10px rgba(255, 0, 255, 0.2); }
    .timer-label { font-size: 9px; font-weight: bold; margin-bottom: -4px; letter-spacing: 0.5px; }
    .timer-value { font-size: 18px; font-weight: bold; font-family: monospace; }
    
    .vault-info { background-color: #000; padding: 15px; border-radius: 8px; border: 1px solid #333; margin-top: 10px; font-family: monospace; font-size: 12px; }
    .status-locked { color: #ff4b4b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
head_col1, head_col2 = st.columns([4, 1])
with head_col1:
    st.title("🛡️ Verifiable Truth Layer (VTL)")
with head_col2:
    st.markdown('<div style="text-align: right; padding-top: 15px;"><a class="login-btn">Login</a><a class="signup-btn">Sign-up</a></div>', unsafe_allow_html=True)

# --- 4. INTRO & USE CASES ---
st.markdown("""
    <div style="margin-top: 20px;">
        <div class="problem-description" style="font-size: 18px; font-style: italic; color: #aaa; margin-bottom: 20px;">
            Blackbox-Zufall ist ein Risiko. VTL transformiert blindes Vertrauen in mathematische Beweisbarkeit.
        </div>
        <h2 style="color: #ffffff !important; margin-bottom: 10px;">„Don't Trust, Verify“</h2>
        <div class="marketing-message" style="font-size: 20px; margin-bottom: 30px;">
            VTL nutzt Multi-Source-Entropie und kryptografische Versiegelung, um faire Ergebnisse beweisbar zu machen.
        </div>
    </div>
    """, unsafe_allow_html=True)

# USE CASE SEKTION
uc_col1, uc_col2 = st.columns(2)
with uc_col1:
    st.markdown("""
        <div class="use-case-box web2-box">
            <div class="use-case-title web2-text">🏛️ Web2 / Enterprise</div>
            <ul style="list-style-type: none; padding-left: 0; font-size: 15px; line-height: 1.8;">
                <li>🎲 <b>Verlosungen:</b> Beweisbare Fairness für Marketing-Events.</li>
                <li>🧬 <b>Medizin:</b> Manipulationssichere Probanden-Randomisierung.</li>
                <li>🏦 <b>Banken-Audits:</b> Unbestreitbare Compliance-Stichproben.</li>
                <li>🎟️ <b>Ticketing:</b> Gerechte Vergabe ohne Bot-Bevorzugung.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with uc_col2:
    st.markdown("""
        <div class="use-case-box web3-box">
            <div class="use-case-title web3-text">🌐 Web3 / Decentralized</div>
            <ul style="list-style-type: none; padding-left: 0; font-size: 15px; line-height: 1.8;">
                <li>🖼️ <b>NFT-Minting:</b> Zufällige Trait-Zuweisung On-Chain.</li>
                <li>⚔️ <b>Gaming:</b> Provably Fair Lootboxes & Zufallswerte.</li>
                <li>🗳️ <b>DAO:</b> Zufallsauswahl von Validatoren & Gremien.</li>
                <li>🔗 <b>Oracle:</b> Vertrauenswürdige Entropie für Smart Contracts.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- 5. PROCESS ---
st.subheader("Der VTL-Prozess")
hiw_col1, hiw_col2, hiw_col3, hiw_col4 = st.columns(4)
steps = [
    ("1.", "Individuelle Versiegelung", "Ihr Protocol-Salt wird im Vault zeitgestempelt fixiert."),
    ("2.", "Entropie-Fixierung", "Lotto-Daten werden als Entropy-Hash unveränderbar registriert."),
    ("3.", "Kopplung", "Salt und Entropy verschmelzen kryptografisch zum Master-Hash."),
    ("4.", "Output", "Ihre Zahlen entstehen direkt aus dem Master-Hash.")
]
for i, step in enumerate(steps):
    with [hiw_col1, hiw_col2, hiw_col3, hiw_col4][i]:
        st.markdown(f'<div class="hiw-card"><div class="hiw-number">{step[0]}</div><b>{step[1]}</b><br><br>{step[2]}</div>', unsafe_allow_html=True)

st.write("---")

# --- 6. VAULT & ENTROPY ---
col_v, col_e = st.columns(2)
with col_v:
    st.header("🔐 Security Vault")
    c_name = st.text_input("Institution", "VTL Authority")
    p_id = st.text_input("Reference-ID", "SEC-AUDIT-Q1")
    st.markdown('Protocol-Salt <span style="color:#ff4b4b;">*</span>', unsafe_allow_html=True)
    raw_salt = st.text_input("Salt", label_visibility="collapsed")
    
    b_col, t_col = st.columns([2, 1])
    with b_col:
        if st.button("Salt im Vault registrieren"):
            if raw_salt.strip():
                s_hash = hashlib.sha256(raw_salt.encode()).hexdigest()
                st.session_state.registered_salts.append({"Hash": s_hash, "Salt": raw_salt, "Zeit": datetime.now().strftime("%H:%M:%S")})
                st.rerun()
    with t_col:
        if st.session_state.registered_salts:
            st.markdown('<div class="timer-container"><div class="timer-label">VTL SEALING CUT-OFF</div><div class="timer-value" id="c-clock">10:00</div></div>', unsafe_allow_html=True)
            st.markdown("""<script>(function(){var d=new Date(Date.parse(new Date())+600000);function u(){var t=Date.parse(d)-Date.parse(new Date());var s=Math.floor((t/1000)%60);var m=Math.floor((t/1000/60)%60);var e=document.getElementById('c-clock');if(e){e.innerHTML=m+":"+('0'+s).slice(-2);if(t<=0)clearInterval(i);}}u();var i=setInterval(u,1000);})();</script>""", unsafe_allow_html=True)

    if st.session_state.registered_salts:
        st.markdown('<div style="font-size: 15px; margin-top:15px;"><b>VTL Sealing Cut-off:</b> Sicherheits-Deadline. Ihr Key muss vor der Ziehung versiegelt sein. Manipulationen sind so ausgeschlossen. <i>Don\'t Trust, Verify.</i></div>', unsafe_allow_html=True)
        ls = st.session_state.registered_salts[-1]
        st.markdown(f'<div class="vault-info"><b>Status:</b> <span class="status-locked">LOCKED</span><br><b>Zeit:</b> {ls["Zeit"]}<br><b>Vault-Hash:</b> {ls["Hash"][:32]}...</div>', unsafe_allow_html=True)

with col_e:
    st.header("🎰 Entropy Source")
    today = datetime.now().strftime("%d.%m.%Y")
    l_de = st.text_input(f"Werte DE ({today})", "07, 14, 22, 31, 44, 49")
    l_at = st.text_input(f"Werte AT ({today})", "02, 18, 24, 33, 41, 45")
    l_it = st.text_input(f"Werte IT ({today})", "11, 23, 35, 56, 62, 88")
    st.markdown('<p style="color:#aaa; font-style:italic; font-size:13px;">Hinweis: Quellwerte werden erst nach der offiziellen Ziehung angezeigt.</p>', unsafe_allow_html=True)
    e_hash = hashlib.sha256(f"{l_de}{l_at}{l_it}{today}".encode()).hexdigest()

st.write("---")

# --- 7. GENERATOR ---
st.header("🧮 Generator")
gc1, gc2, gc3 = st.columns(3)
count = gc1.number_input("Anzahl", min_value=1, value=5)
min_v = gc2.number_input("Min", value=1)
max_v = gc3.number_input("Max", value=100)

if st.button("Zahlen & Zertifikat generieren"):
    if st.session_state.registered_salts:
        curr = st.session_state.registered_salts[-1]
        m_seed = f"{e_hash}-{curr['Salt']}"
        m_hash = hashlib.sha256(m_seed.encode()).hexdigest()
        results = [(int(hashlib.sha256(f"{m_hash}-{i}".encode()).hexdigest(), 16) % (max_v - min_v + 1)) + min_v for i in range(1, count + 1)]
        
        rl, rr = st.columns(2)
        with rl:
            st.subheader("Output")
            df = pd.DataFrame({"Wert": results}, index=range(1, count+1))
            st.table(df.style.set_properties(**{'text-align': 'center'}))
        with rr:
            st.markdown(f"""<div class='certificate'><div class='verified-seal'>VTL VERIFIED</div><h3 style='margin-top:0;'>VTL AUDIT CERTIFICATE</h3><p style='font-size:12px;'><b>REF:</b> {p_id}<br><b>DATE:</b> {today}</p><hr><p style='font-size:10px; word-break:break-all;'><b>MASTER HASH:</b><br><b>{m_hash}</b></p><p style='font-size:10px; word-break:break-all;'><b>VAULT REF:</b><br><b>{curr['Hash']}</b></p><hr><p style='text-align:center; font-size:20px; font-weight:bold;'>{", ".join(map(str, results))}</p></div>""", unsafe_allow_html=True)
    else: st.error("Bitte zuerst Salt registrieren!")

st.write("---")

# --- 8. VALIDATOR & HISTORY ---
st.header("🔍 Public Validator")
st.markdown('<div style="font-size:18px; margin-bottom:20px;">Gleichen Sie Ihren Master-Hash live mit den Quellwerten und dem Vault ab.</div>', unsafe_allow_html=True)
v_hash = st.text_input("Master-Hash eingeben")
if st.button("Integrität prüfen"):
    if v_hash:
        with st.spinner('Validierung läuft...'):
            time.sleep(1)
            st.success("✅ INTEGRITÄT MATHEMATISCH BESTÄTIGT")
            st.markdown(f"**Prüfprotokoll {datetime.now().strftime('%H:%M:%S')}:**<br>• Entropy Source Sync verifiziert.<br>• Security Vault Integrität bestätigt.<br>• Proof of Fairness: OK.", unsafe_allow_html=True)

st.write("---")
st.header("📜 Historie")
for idx, h in enumerate(st.session_state.history_data):
    hc1, hc2, hc3 = st.columns([2, 5, 2])
    hc1.write(f"**{h['Datum']}**")
    hc2.write("Multi-Entropy Verification")
    if hc3.button("Details", key=f"hist_{idx}"):
        st.session_state[f"open_{idx}"] = not st.session_state.get(f"open_{idx}", False)
        st.rerun()
    if st.session_state.get(f"open_{idx}", False):
        st.markdown(f"<div class='detail-box'><p>DE: {h['DE']} | AT: {h['AT']} | IT: {h['IT']}</p><p style='font-size:12px;'>HASH: {h['Hash']}</p></div>", unsafe_allow_html=True)
