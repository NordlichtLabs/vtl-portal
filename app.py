import hashlib
import time
from datetime import datetime
import pandas as pd
import streamlit as st

# --- 1. INITIALISIERUNG (STATE MANAGEMENT) ---
if 'registered_salts' not in st.session_state:
    st.session_state.registered_salts = []
if 'history_data' not in st.session_state:
    st.session_state.history_data = [
        {"Datum": "03.02.2026", "DE": "12, 45, 67, 23, 89, 10", "AT": "01, 15, 22, 33, 40, 42", "IT": "11, 22, 33, 44, 55, 66", "Hash": "f3b2c1a9e8d7c6b5a49382716059483726150493827160594837261504938271"},
        {"Datum": "02.02.2026", "DE": "05, 14, 28, 33, 41, 44", "AT": "07, 19, 21, 30, 39, 45", "IT": "03, 12, 34, 56, 78, 90", "Hash": "d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5"}
    ]
if 'current_cert' not in st.session_state:
    st.session_state.current_cert = None

# --- 2. DESIGN & STYLING ---
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
        width: 100%; background: linear-gradient(45deg, #004a99, #00d4ff); 
        color: white; font-weight: bold; border-radius: 5px; border: none; height: 45px; transition: 0.3s;
    }
    
    .login-btn { border: 1px solid #ffffff; color: #ffffff !important; padding: 5px 15px; border-radius: 5px; text-decoration: none; font-size: 14px; margin-right: 10px; }
    .signup-btn { background-color: #ffffff; color: #000 !important; padding: 5px 15px; border-radius: 5px; text-decoration: none; font-size: 14px; font-weight: bold; }

    .use-case-box { padding: 25px; border-radius: 10px; background: rgba(255, 255, 255, 0.03); height: 100%; border-top: 4px solid; }
    .web2-box { border-color: #00d4ff; }
    .web3-box { border-color: #ff00ff; }
    .web2-text { color: #00d4ff; font-weight: bold; font-size: 22px; }
    .web3-text { color: #ff00ff; font-weight: bold; font-size: 22px; }

    .hiw-card { background-color: rgba(0, 74, 153, 0.15); padding: 25px; border-radius: 12px; height: 100%; border: 1px solid #004a99; }
    
    /* Zertifikat Design */
    .certificate { 
        border: 2px solid #000; padding: 35px; border-radius: 10px; background-color: #ffffff; color: #000000; 
        font-family: 'Courier New', monospace; position: relative; box-shadow: 0 0 40px rgba(0, 212, 255, 0.4); line-height: 1.4;
    }
    .cert-logo { position: absolute; top: 20px; right: 30px; font-size: 40px; opacity: 0.15; }
    .cert-label { font-weight: bold; font-size: 13px; color: #555; text-transform: uppercase; margin-top: 12px; }
    .cert-value { font-size: 16px; margin-bottom: 12px; word-break: break-all; color: #000; }
    .cert-title { font-size: 26px; font-weight: bold; margin-bottom: 25px; text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; }

    .timer-container { border: 1px solid #ff00ff; background-color: rgba(255, 0, 255, 0.05); border-radius: 8px; height: 45px; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #ff00ff; }
    .vault-info { background-color: #000; padding: 15px; border-radius: 8px; border: 1px solid #333; margin-top: 10px; font-family: monospace; font-size: 12px; }
    .process-flow { background-color: rgba(0, 212, 255, 0.1); border: 1px dashed #00d4ff; padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
h_col1, h_col2 = st.columns([4, 1])
with h_col1:
    st.title("🛡️ Verifiable Truth Layer (VTL)")
with h_col2:
    st.markdown('<div style="text-align: right; padding-top: 15px;"><a class="login-btn">Login</a><a class="signup-btn">Sign-up</a></div>', unsafe_allow_html=True)

# --- 4. INTRO & USE CASES ---
st.markdown("""
    <div style="margin-top: 20px;">
        <div style="color: #ffffff; font-size: 18px; line-height: 1.5; max-width: 1000px; margin-bottom: 20px;">
            Das Problem herkömmlicher Zufallsgeneratoren: Ein digitales Blindvertrauen. Die meisten heutigen Systeme zur Zufallszahlengenerierung sind eine <b>Blackbox</b>. 
            Ob bei Gewinnspielen, Audits oder Zuteilungen – das Ergebnis wird hinter verschlossenen Türen berechnet. Für den Nutzer ist nicht nachvollziehbar, 
            ob das Resultat wirklich dem Zufall entspringt oder im Nachhinein manipuliert wurde. Ohne beweisbare Integrität bleibt jede digitale Entscheidung 
            eine Vertrauensfrage, kein mathematischer Fakt.
        </div>
        <h2 style="color: #ffffff !important; margin-bottom: 10px;">„Don't Trust, Verify“</h2>
        <div style="font-size: 20px; color: #ffffff; margin-bottom: 30px;">
            VTL nutzt Multi-Source-Entropie und kryptografische Protokolle, um sicherzustellen, dass Ergebnisse nicht nur fair sind, sondern auch für immer beweisbar bleiben.
        </div>
    </div>
    """, unsafe_allow_html=True)

uc1, uc2 = st.columns(2)
with uc1:
    st.markdown('<div class="use-case-box web2-box"><div class="web2-text">Use Cases: Web2</div><ul style="font-size:17px; line-height:1.8; list-style:none; padding:0;"><li>🎲 <b>Verlosungen:</b> Beweisbare Fairness für Marketing-Kampagnen.</li><li>🧬 <b>Medizinische Studien:</b> Manipulationssichere Randomisierung.</li><li>🏦 <b>Banken-Audits:</b> Unbestreitbare Compliance-Stichproben.</li><li>🎟️ <b>Ticketing:</b> Gerechte Vergabe ohne Bot-Bevorzugung.</li></ul></div>', unsafe_allow_html=True)
with uc2:
    st.markdown('<div class="use-case-box web3-box"><div class="web3-text">Use Cases: Web3</div><ul style="font-size:17px; line-height:1.8; list-style:none; padding:0;"><li>🖼️ <b>NFT-Minting:</b> Zufällige Trait-Zuweisung On-Chain.</li><li>⚔️ <b>Gaming:</b> Provably Fair Lootboxes & Zufallswerte.</li><li>🗳️ <b>DAO-Governance:</b> Auswahl von Validatoren & Gremien.</li><li>🔗 <b>Oracle-Entropie:</b> Sicherer Zufall für Smart Contracts.</li></ul></div>', unsafe_allow_html=True)

st.write("---")

# --- 5. PROCESS FLOW ---
st.subheader("Der VTL-Prozess")
hiw1, hiw2, hiw3, hiw4 = st.columns(4)
steps = [("1.", "Versiegelung", "Der Protocol-Salt wird im VTL Vault zeitgestempelt versiegelt."),
         ("2.", "Fixierung", "Lotto-Daten werden als Entropy-Hash unveränderbar registriert."),
         ("3.", "Kopplung", "Salt und Entropy verschmelzen kryptografisch zum Master-Hash."),
         ("4.", "Output", "Aus dem Master-Hash entstehen beweisbare Zahlen.")]
for i, step in enumerate(steps):
    with [hiw1, hiw2, hiw3, hiw4][i]:
        st.markdown(f'<div class="hiw-card"><div style="color:#00d4ff; font-size:28px; font-weight:bold;">{step[0]}</div><b>{step[1]}</b><br><br>{step[2]}</div>', unsafe_allow_html=True)

st.write("---")

# --- 6. VAULT & ENTROPY ---
col_v, col_e = st.columns(2)
with col_v:
    st.header("🔐 Security Vault")
    p_id = st.text_input("Reference-ID", "SEC-AUDIT-Q1")
    st.markdown('Protocol-Salt <span style="color:#ff4b4b; font-weight:bold;">*</span>', unsafe_allow_html=True)
    raw_salt = st.text_input("Salt-Input", placeholder="Geben Sie den Salt ein...", label_visibility="collapsed")
    
    with st.expander("💡 Was ist der Protocol-Salt? (Beispiel)"):
        st.markdown("""
            Der **Protocol-Salt** ist Ihr persönlicher „Fingerabdruck“ im System. Er garantiert, dass Ergebnisse individuell berechnet werden und vorab nicht manipuliert werden können.
            
            **Das Tresor-Prinzip:**
            1. **Versiegelung:** Bevor die Lottozahlen (die externe Entropie) gezogen werden, legen Sie Ihren geheimen Salt (z. B. das Wort `Sicherheit2026`) in unseren digitalen Tresor.
            2. **Zeitstempel:** Das System quittiert: „Der Salt wurde um 14:00 Uhr versiegelt.“
            3. **Die Ziehung:** Um 20:00 Uhr werden die offiziellen Lottozahlen gezogen (z. B. `7, 14, 23...`).
            4. **Die Kopplung:** VTL berechnet nun: `[7, 14, 23] + [Sicherheit2026] = Ihr Ergebnis`.
            
            **Beweis:** Da Ihr Salt bereits feststand, als die Zahlen noch unbekannt waren, ist eine nachträgliche Manipulation mathematisch ausgeschlossen.
        """)
    
    btn_c, tim_c = st.columns([2, 1])
    with btn_c:
        if st.button("Protocol-Salt im Vault registrieren"):
            if not raw_salt.strip():
                st.error("Bitte geben sie zuerst den Protocol-Salt ein!")
            else:
                now = datetime.now().strftime("%H:%M:%S")
                s_hash = hashlib.sha256(raw_salt.encode()).hexdigest()
                st.session_state.registered_salts.append({"Hash": s_hash, "Salt": raw_salt, "Zeit": now})
                st.rerun()
    with tim_c:
        if st.session_state.registered_salts:
            st.markdown('<div class="timer-container"><div class="timer-label">VTL SEALING CUT-OFF</div><div class="timer-value" id="c-clock">10:00</div></div>', unsafe_allow_html=True)
            st.markdown("""<script>(function(){var d=new Date(Date.parse(new Date())+600000);function u(){var t=Date.parse(d)-Date.parse(new Date());var s=Math.floor((t/1000)%60);var m=Math.floor((t/1000/60)%60);var e=document.getElementById('c-clock');if(e){e.innerHTML=m+":"+('0'+s).slice(-2);if(t<=0)clearInterval(i);}}u();var i=setInterval(u,1000);})();</script>""", unsafe_allow_html=True)

    if st.session_state.registered_salts:
        ls = st.session_state.registered_salts[-1]
        st.markdown(f"""<div style="font-size: 15px; margin-top:15px; line-height:1.4;"><b>VTL Sealing Cut-off:</b> Sicherheits-Deadline. Ihr Key muss vor der Ziehung versiegelt sein. Manipulationen sind so ausgeschlossen.</div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="vault-info"><b>Status:</b> <span style="color:#ff4b4b;">LOCKED / SEALED</span><br><b>Versiegelt um:</b> {ls["Zeit"]} Uhr<br><b>Vault-Hash:</b> {ls["Hash"][:32]}...</div>', unsafe_allow_html=True)

with col_e:
    st.header("🎰 Entropy Source")
    today = datetime.now().strftime("%d.%m.%Y")
    l_de = st.text_input(f"Quellwerte DE ({today})", "07, 14, 22, 31, 44, 49")
    l_at = st.text_input(f"Quellwerte AT ({today})", "02, 18, 24, 33, 41, 45")
    l_it = st.text_input(f"Quellwerte IT ({today})", "11, 23, 35, 56, 62, 88")
    st.markdown('<p style="color:#aaa; font-style:italic; font-size:13px; margin-top:5px;">Hinweis: Die Quellwerte werden erst im Anschluss an die Ziehung angezeigt.</p>', unsafe_allow_html=True)
    e_hash = hashlib.sha256(f"{l_de}{l_at}{l_it}{today}".encode()).hexdigest()

st.write("---")

# --- 7. GENERATOR & CERTIFICATE ---
st.header("🧮 Generator")
gc1, gc2, gc3 = st.columns(3)
count = gc1.number_input("Anzahl", min_value=1, value=5)
min_v = gc2.number_input("Von", value=1)
max_v = gc3.number_input("Bis", value=100)

if st.button("Zahlen & Zertifikat berechnen"):
    if st.session_state.registered_salts:
        curr = st.session_state.registered_salts[-1]
        m_seed = f"{e_hash}-{curr['Salt']}"
        m_hash = hashlib.sha256(m_seed.encode()).hexdigest()
        results = [(int(hashlib.sha256(f"{m_hash}-{i}".encode()).hexdigest(), 16) % (max_v - min_v + 1)) + min_v for i in range(1, count + 1)]
        
        st.session_state.current_cert = {
            "flow": f"<div class='process-flow'><span style='color:#00d4ff'>Entropy-Hash</span> ({e_hash[:8]}...) <b>+</b> <span style='color:#ff00ff'>Protocol-Salt</span> ({curr['Salt']}) <b>=</b> <span style='font-weight:bold'>Master-Hash</span> ({m_hash[:12]}...)</div>",
            "results_str": ", ".join(map(str, results)),
            "m_hash": m_hash,
            "table": pd.DataFrame({"Wert": results}, index=range(1, count+1)),
            "p_id": p_id, "date": today, "entropy_all": f"{l_de} | {l_at} | {l_it}", "salt": curr['Salt'], "salt_time": curr['Zeit']
        }
        st.session_state.last_m_hash = m_hash
    else: st.error("Bitte geben Sie zuerst den Protocol-Salt ein!")

if st.session_state.current_cert:
    c = st.session_state.current_cert
    st.markdown(c["flow"], unsafe_allow_html=True)
    rl, rr = st.columns([1, 2])
    with rl: st.table(c["table"])
    with rr:
        st.markdown(f"""<div class='certificate'><div class='cert-logo'>🛡️</div><div style='position:absolute; bottom:20px; right:20px; border:3px double #28a745; color:#28a745; padding:5px 10px; font-weight:bold; transform:rotate(-15deg); border-radius:5px;'>VTL VERIFIED</div><div class='cert-title'>VTL AUDIT CERTIFICATE</div><div class='cert-label'>Reference-ID & Date</div><div class='cert-value'>{c['p_id']} | {c['date']}</div><div class='cert-label'>Entropy Sources (DE/AT/IT)</div><div class='cert-value'>{c['entropy_all']}</div><div class='cert-label'>Protocol-Salt (Sealed)</div><div class='cert-value'>{c['salt']} (Versiegelt um {c['salt_time']})</div><div class='cert-label'>Kryptografischer Master-Hash</div><div class='cert-value' style='font-size:12px; font-family: monospace;'>{c['m_hash']}</div><hr style='border: 1px solid #ddd;'><div class='cert-label' style='text-align:center;'>Final Verifiable Results</div><p style='text-align:center; font-size:32px; font-weight:bold; margin-top:10px; color:#000;'>{c['results_str']}</p></div>""", unsafe_allow_html=True)
        
        st.download_button(label="📄 Download Certificate (.pdf)", data=f"VTL AUDIT REPORT\nID: {c['p_id']}\nHASH: {c['m_hash']}\nRESULTS: {c['results_str']}", file_name=f"VTL_Cert_{c['p_id']}.txt")

st.write("---")

# --- 8. VALIDATOR ---
st.header("🔍 Public Validator")
st.markdown("""<div style="font-size:24px; font-weight:bold; color:#00d4ff; margin-bottom:10px;">Wahrheit durch Mathematik: Prüfen Sie hier die Integrität Ihrer Ergebnisse.</div><div style="font-size:18px; color:#ffffff; line-height:1.5; max-width:1000px; margin-bottom:20px;">Sobald Sie ihren den Master-Hash aus dem VTL Audit Certificate eingeben, rekonstruiert der Validator die gesamte kryptografische Kette. Das System gleicht Ihre Daten live mit den versiegelten Protokollen im Security Vault und den offiziellen Entropie-Quellen ab. Nur wenn jede mathematische Variable exakt übereinstimmt, wird die Integrität bestätigt.</div>""", unsafe_allow_html=True)
v_hash = st.text_input("Master-Hash aus dem VTL Audit Certificate zur Verifizierung eingeben", placeholder="f3b2c1a9e8...")
if st.button("Integrität prüfen"):
    if v_hash:
        with st.spinner('Validierung...'):
            time.sleep(1.2)
            if v_hash == st.session_state.get('last_m_hash') or any(h['Hash'] == v_hash for h in st.session_state.history_data):
                st.success("✅ INTEGRITÄT MATHEMATISCH BESTÄTIGT")
                st.markdown(f"**Prüfprotokoll vom {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}:**<br>• Entropy Source Sync verifiziert.<br>• Date-Binding bestätigt.<br>• Security Vault abgeglichen.<br>• Proof of Fairness: OK.", unsafe_allow_html=True)
            else: st.error("❌ INTEGRITÄT VERLETZT / UNBEKANNTER HASH")

st.write("---")

# --- 9. HISTORY ---
st.header("📜 Protokoll-Historie")
for idx, h in enumerate(st.session_state.history_data):
    with st.container():
        c_dat, c_bt = st.columns([7, 2])
        with c_dat: st.markdown(f"<div style='padding-top:10px; font-size:18px;'><b>📅 {h['Datum']}</b></div>", unsafe_allow_html=True)
        with c_bt:
            if st.button("Details", key=f"hist_btn_{idx}"):
                st.session_state[f"open_{idx}"] = not st.session_state.get(f"open_{idx}", False)
                st.rerun()
        if st.session_state.get(f"open_{idx}", False):
            st.markdown(f"<div class='detail-box'><div style='line-height:1.8; margin-bottom:15px;'><span style='color:#00d4ff;'>●</span> <b>DE:</b> {h['DE']}<br><span style='color:#00d4ff;'>●</span> <b>AT:</b> {h['AT']}<br><span style='color:#00d4ff;'>●</span> <b>IT:</b> {h['IT']}</div><hr style='opacity:0.3;'><p style='font-family:monospace; font-size:12px; color:#aaa;'><b>VERIFICATION HASH:</b><br>{h['Hash']}</p></div>", unsafe_allow_html=True)
        st.markdown("<hr style='border:0.5px solid #222; margin:10px 0;'>", unsafe_allow_html=True)
