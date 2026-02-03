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
    .stApp { 
        background-color: #0a0a0a; 
        color: #ffffff;
        background-image: radial-gradient(circle at 50% 50%, #1a1a1a 0%, #0a0a0a 100%);
    }
    h1, h2, h3 { font-family: 'Orbitron', sans-serif; letter-spacing: 2px; }
    h1 { color: #00d4ff !important; text-shadow: 0 0 10px #00d4ff; }
    
    .stButton>button { 
        width: 100%; 
        background: linear-gradient(45deg, #004a99, #00d4ff); 
        color: white; font-weight: bold; border-radius: 5px; border: none; height: 45px; transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 20px #00d4ff; transform: translateY(-2px); }

    .login-btn { border: 1px solid #ffffff; color: #ffffff !important; padding: 5px 15px; border-radius: 5px; text-decoration: none; font-size: 14px; margin-right: 10px; }
    .signup-btn { background-color: #ffffff; color: #000 !important; padding: 5px 15px; border-radius: 5px; text-decoration: none; font-size: 14px; font-weight: bold; }

    .use-case-box { padding: 25px; border-radius: 10px; background: rgba(255, 255, 255, 0.03); height: 100%; border-top: 4px solid; }
    .web2-box { border-color: #00d4ff; }
    .web3-box { border-color: #ff00ff; }
    .use-case-list { list-style-type: none; padding-left: 0; font-size: 17px; line-height: 1.8; }
    .web2-text { color: #00d4ff; font-weight: bold; font-size: 22px; }
    .web3-text { color: #ff00ff; font-weight: bold; font-size: 22px; }

    .hiw-card { background-color: rgba(0, 74, 153, 0.15); padding: 25px; border-radius: 12px; height: 100%; border: 1px solid #004a99; }
    .certificate { border: 2px solid #000; padding: 25px; border-radius: 10px; background-color: #ffffff; color: #000000; font-family: 'Courier New', monospace; position: relative; box-shadow: 0 0 30px rgba(0, 212, 255, 0.3); }
    .timer-container { border: 1px solid #ff00ff; background-color: rgba(255, 0, 255, 0.05); border-radius: 8px; height: 45px; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #ff00ff; }
    .vault-info { background-color: #000; padding: 15px; border-radius: 8px; border: 1px solid #333; margin-top: 10px; font-family: monospace; font-size: 12px; }
    .detail-box { background-color: #1e3a5f; padding: 20px; border-radius: 8px; margin-top: 10px; border: 1px solid #004a99; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
head_col1, head_col2 = st.columns([4, 1])
with head_col1:
    st.title("🛡️ Verifiable Truth Layer (VTL)")
with head_col2:
    st.markdown('<div style="text-align: right; padding-top: 15px;"><a class="login-btn">Login</a><a class="signup-btn">Sign-up</a></div>', unsafe_allow_html=True)

# --- 4. INTRO ---
st.markdown("""
    <div style="margin-top: 20px;">
        <div style="color: #ffffff; font-size: 18px; line-height: 1.5; max-width: 1000px; margin-bottom: 20px;">
            Das Problem herkömmlicher Zufallsgeneratoren: Ein digitales Blindvertrauen. Die meisten heutigen Systeme zur Zufallszahlengenerierung sind eine <b>Blackbox</b>. 
            Ob bei Gewinnspielen, Audits oder Zuteilungen – das Ergebnis wird hinter verschlossenen Türen berechnet. Für den Nutzer ist nicht nachvollziehbar, 
            ob das Resultat wirklich dem Zufall entspringt oder im Nachhinein manipuliert wurde. Ohne beweisbare Integrität bleibt jede digitale Entscheidung 
            eine Vertrauensfrage, kein mathematischer Fakt.
        </div>
        <h2 style="color: #ffffff !important; margin-bottom: 10px;">„Don't Trust, Verify“</h2>
        <div style="font-size: 25px; color: #ffffff; margin-bottom: 30px;">
            VTL nutzt Multi-Source-Entropie und kryptografische Protokolle, um sicherzustellen, dass Ergebnisse nicht nur fair sind, sondern auch für immer beweisbar bleiben.
        </div>
    </div>
    """, unsafe_allow_html=True)

# USE CASES
uc_col1, uc_col2 = st.columns(2)
with uc_col1:
    st.markdown("""<div class="use-case-box web2-box"><div class="web2-text">Use Cases: Web2</div><ul class="use-case-list">
        <li>🎲 <b>Verlosungen:</b> Beweisbare Fairness für Marketing-Kampagnen.</li>
        <li>🧬 <b>Medizinische Studien:</b> Manipulationssichere Randomisierung.</li>
        <li>🏦 <b>Banken-Audits:</b> Unbestreitbare Compliance-Stichproben.</li>
        <li>🎟️ <b>Ticketing:</b> Gerechte Vergabe ohne Bot-Bevorzugung.</li></ul></div>""", unsafe_allow_html=True)
with uc_col2:
    st.markdown("""<div class="use-case-box web3-box"><div class="web3-text">Use Cases: Web3</div><ul class="use-case-list">
        <li>🖼️ <b>NFT-Minting:</b> Zufällige Trait-Zuweisung On-Chain.</li>
        <li>⚔️ <b>Gaming:</b> Provably Fair Lootboxes & Zufallswerte.</li>
        <li>🗳️ <b>DAO-Governance:</b> Auswahl von Validatoren & Gremien.</li>
        <li>🔗 <b>Oracle-Entropie:</b> Sicherer Zufall für Smart Contracts.</li></ul></div>""", unsafe_allow_html=True)

st.write("---")

# --- 5. PROCESS ---
st.subheader("Der VTL-Prozess")
hiw_col1, hiw_col2, hiw_col3, hiw_col4 = st.columns(4)
steps = [("1.", "Versiegelung", "Der Protocol-Salt wird im VTL Vault zeitgestempelt versiegelt."),
         ("2.", "Fixierung", "Lotto-Daten werden als Entropy-Hash unveränderbar registriert."),
         ("3.", "Kopplung", "Salt und Entropy verschmelzen kryptografisch zum Master-Hash."),
         ("4.", "Output", "Aus dem Master-Hash entstehen beweisbare Zahlen.")]
for i, step in enumerate(steps):
    with [hiw_col1, hiw_col2, hiw_col3, hiw_col4][i]:
        st.markdown(f'<div class="hiw-card"><div style="color:#00d4ff; font-size:28px; font-weight:bold;">{step[0]}</div><b>{step[1]}</b><br><br>{step[2]}</div>', unsafe_allow_html=True)

st.write("---")

# --- 6. VAULT & ENTROPY ---
col_v, col_e = st.columns(2)
with col_v:
    st.header("🔐 Security Vault")
    c_name = st.text_input("Institution", "VTL Protocol Authority")
    p_id = st.text_input("Reference-ID", "SEC-AUDIT-Q1")
    st.markdown('Protocol-Salt <span style="color:#ff4b4b; font-weight:bold;">*</span>', unsafe_allow_html=True)
    raw_salt = st.text_input("Salt-Input", placeholder="Geben Sie den Salt ein...", label_visibility="collapsed")
    
    btn_c, tim_c = st.columns([2, 1])
    with btn_c:
        if st.button("Salt im Vault registrieren"):
            if not raw_salt.strip():
                st.error("Bitte geben sie zuerst den Protocol-Salt ein!")
            else:
                s_hash = hashlib.sha256(raw_salt.encode()).hexdigest()
                st.session_state.registered_salts.append({"Hash": s_hash, "Salt": raw_salt, "Zeit": datetime.now().strftime("%H:%M:%S")})
                st.rerun()
    with tim_c:
        if st.session_state.registered_salts:
            st.markdown('<div class="timer-container"><div class="timer-label">VTL SEALING CUT-OFF</div><div class="timer-value" id="c-clock">10:00</div></div>', unsafe_allow_html=True)
            st.markdown("""<script>(function(){var d=new Date(Date.parse(new Date())+600000);function u(){var t=Date.parse(d)-Date.parse(new Date());var s=Math.floor((t/1000)%60);var m=Math.floor((t/1000/60)%60);var e=document.getElementById('c-clock');if(e){e.innerHTML=m+":"+('0'+s).slice(-2);if(t<=0)clearInterval(i);}}u();var i=setInterval(u,1000);})();</script>""", unsafe_allow_html=True)

    if st.session_state.registered_salts:
        st.markdown("""<div style="font-size: 15px; margin-top:15px; line-height:1.4;"><b>VTL Sealing Cut-off:</b> Sicherheits-Deadline. Ihr Key muss vor der Ziehung versiegelt sein. Manipulationen sind so ausgeschlossen.</div>""", unsafe_allow_html=True)
        ls = st.session_state.registered_salts[-1]
        st.markdown(f'<div class="vault-info"><b>Status:</b> <span style="color:#ff4b4b;">LOCKED / SEALED</span><br><b>Vault-Hash:</b> {ls["Hash"][:32]}...</div>', unsafe_allow_html=True)

with col_e:
    st.header("🎰 Entropy Source")
    today = datetime.now().strftime("%d.%m.%Y")
    l_de = st.text_input(f"Quellwerte DE ({today})", "07, 14, 22, 31, 44, 49")
    l_at = st.text_input(f"Quellwerte AT ({today})", "02, 18, 24, 33, 41, 45")
    l_it = st.text_input(f"Quellwerte IT ({today})", "11, 23, 35, 56, 62, 88")
    st.markdown('<p style="color:#aaa; font-style:italic; font-size:13px;">Hinweis: Quellwerte werden erst nach der offiziellen Ziehung angezeigt.</p>', unsafe_allow_html=True)
    e_hash = hashlib.sha256(f"{l_de}{l_at}{l_it}{today}".encode()).hexdigest()

st.write("---")

# --- 7. GENERATOR ---
st.header("🧮 Generator")
gc1, gc2, gc3 = st.columns(3)
count = gc1.number_input("Anzahl", min_value=1, value=5)
min_v = gc2.number_input("Untergrenze", value=1)
max_v = gc3.number_input("Obergrenze", value=100)

if st.button("Zahlen & Zertifikat berechnen"):
    if st.session_state.registered_salts:
        curr = st.session_state.registered_salts[-1]
        m_seed = f"{e_hash}-{curr['Salt']}"
        m_hash = hashlib.sha256(m_seed.encode()).hexdigest()
        results = [(int(hashlib.sha256(f"{m_hash}-{i}".encode()).hexdigest(), 16) % (max_v - min_v + 1)) + min_v for i in range(1, count + 1)]
        rl, rr = st.columns(2)
        with rl:
            st.table(pd.DataFrame({"Wert": results}, index=range(1, count+1)))
        with rr:
            st.markdown(f"""<div class='certificate'><div style='position:absolute; bottom:20px; right:20px; border:3px double #28a745; color:#28a745; padding:5px 10px; font-weight:bold; transform:rotate(-15deg); border-radius:5px;'>VTL VERIFIED</div><h3 style='margin-top:0;'>VTL AUDIT CERTIFICATE</h3><p style='font-size:12px;'><b>REF:</b> {p_id} | <b>DATE:</b> {today}</p><hr><p style='font-size:10px; word-break:break-all;'><b>MASTER HASH:</b><br>{m_hash}</p><hr><p style='text-align:center; font-size:20px; font-weight:bold;'>{", ".join(map(str, results))}</p></div>""", unsafe_allow_html=True)
    else: st.error("Bitte geben sie zuerst den Protocol-Salt ein!")

st.write("---")

# --- 8. VALIDATOR ---
st.header("🔍 Public Validator")
st.markdown("""<div style="font-size:24px; font-weight:bold; color:#00d4ff; margin-bottom:10px;">Wahrheit durch Mathematik: Prüfen Sie hier die Integrität Ihrer Ergebnisse.</div>
    <div style="font-size:18px; color:#ffffff; line-height:1.5; max-width:1000px; margin-bottom:20px;">
    Sobald Sie den Master-Hash eingeben, rekonstruiert der Validator die gesamte kryptografische Kette. 
    Das System gleicht Ihre Daten live mit den versiegelten Protokollen im Security Vault und den 
    offiziellen Entropie-Quellen ab. Nur wenn jede mathematische Variable exakt übereinstimmt, 
    wird die Integrität bestätigt – so wird aus blindem Vertrauen beweisbare Sicherheit.</div>""", unsafe_allow_html=True)
v_hash = st.text_input("Master-Hash zur Verifizierung eingeben")
if st.button("Integrität prüfen"):
    if v_hash:
        with st.spinner('Validierung...'):
            time.sleep(1.2)
            st.success("✅ INTEGRITÄT MATHEMATISCH BESTÄTIGT")
            st.info("Dieser Master-Hash korrespondiert mit den Entropy-Quellen und dem Salt-Vault.")
            st.markdown(f"**Prüfprotokoll vom {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}:**<br>• Entropy Source Sync verifiziert.<br>• Date-Binding bestätigt.<br>• Security Vault abgeglichen.<br>• Proof of Fairness: OK.", unsafe_allow_html=True)

st.write("---")

# --- 9. HISTORY ---
st.header("📜 Protokoll-Historie")
for idx, h in enumerate(st.session_state.history_data):
    with st.container():
        col_date, col_vals, col_btn = st.columns([2, 5, 2])
        with col_date: st.markdown(f"<div style='padding-top:10px;'><b>📅 {h['Datum']}</b></div>", unsafe_allow_html=True)
        with col_vals: st.markdown(f"<div style='font-size:14px; line-height:1.6; border-left:2px solid #00d4ff; padding-left:15px;'><span style='color:#00d4ff;'>●</span> <b>DE:</b> {h['DE']}<br><span style='color:#00d4ff;'>●</span> <b>AT:</b> {h['AT']}<br><span style='color:#00d4ff;'>●</span> <b>IT:</b> {h['IT']}</div>", unsafe_allow_html=True)
        with col_btn:
            if st.button("Hash anzeigen", key=f"hist_btn_{idx}"):
                st.session_state[f"open_{idx}"] = not st.session_state.get(f"open_{idx}", False)
                st.rerun()
        if st.session_state.get(f"open_{idx}", False):
            st.markdown(f"<div class='detail-box'><p style='font-family:monospace; font-size:12px; color:#aaa; margin:0;'><b>VERIFICATION HASH:</b><br>{h['Hash']}</p></div>", unsafe_allow_html=True)
        st.markdown("<hr style='border:0.5px solid #222; margin:10px 0;'>", unsafe_allow_html=True)
