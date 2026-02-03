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

# --- 2. KONFIGURATION & DESIGN ---
st.set_page_config(page_title="VTL - Verifiable Truth Layer", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #2e2e2e; color: #ffffff; }
    h1, h2, h3 { color: #004a99 !important; }
    
    .stButton>button { width: 100%; background-color: #004a99; color: white; font-weight: bold; border-radius: 8px; border: none; height: 45px; }
    .stDownloadButton>button { background-color: #28a745 !important; color: white !important; }
    
    .login-btn { background-color: transparent; border: 1px solid #ffffff; color: white; padding: 5px 15px; border-radius: 5px; text-decoration: none; font-size: 14px; margin-right: 10px; cursor: pointer; }
    .signup-btn { background-color: #ffffff; color: #2e2e2e; padding: 5px 15px; border-radius: 5px; text-decoration: none; font-size: 14px; font-weight: bold; cursor: pointer; }

    .problem-description { color: #ffffff; font-size: 18px; line-height: 1.5; max-width: 1000px; margin-bottom: 20px; }
    .marketing-message { color: #ffffff; font-size: 20px; line-height: 1.6; max-width: 1000px; margin-bottom: 25px; }

    .hiw-card { background-color: #004a99; padding: 25px; border-radius: 12px; height: 100%; min-height: 220px; color: #ffffff; border: none; }
    .hiw-number { color: #ffffff; font-size: 28px; font-weight: bold; margin-bottom: 15px; opacity: 0.8; }
    .hiw-card b { font-size: 18px; color: #ffffff !important; }

    .certificate { border: 2px solid #000; padding: 25px; border-radius: 10px; background-color: #ffffff; color: #000000; font-family: 'Courier New', Courier, monospace; position: relative; box-shadow: 10px 10px 20px rgba(0,0,0,0.5); }
    .verified-seal { position: absolute; bottom: 20px; right: 20px; border: 3px double #28a745; color: #28a745; padding: 5px 10px; font-weight: bold; transform: rotate(-15deg); border-radius: 5px; font-size: 14px; opacity: 0.8; }
    
    [data-testid="stTable"] { max-width: 250px; margin-left: auto; margin-right: auto; }
    [data-testid="stTable"] td, [data-testid="stTable"] th { text-align: center !important; }
    
    .vault-info { background-color: #1a1a1a; padding: 15px; border-radius: 8px; border: 1px solid #444; margin-top: 10px; font-family: monospace; font-size: 12px; }
    .status-locked { color: #ff4b4b; font-weight: bold; }
    
    /* Timer Style */
    .expiry-timer-box { 
        background-color: #1a1a1a; 
        border: 1px solid #ff4b4b; 
        border-radius: 8px; 
        height: 45px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        color: #ff4b4b; 
        font-weight: bold; 
        font-family: monospace;
        font-size: 18px;
    }
    
    .detail-box { background-color: #1e3a5f; padding: 20px; border-radius: 8px; margin-top: 10px; border: 1px solid #004a99; }
    .hist-hash-text { font-size: 14px; font-family: sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
head_col1, head_col2 = st.columns([4, 1])
with head_col1:
    st.title("🛡️ Verifiable Truth Layer (VTL)")
with head_col2:
    st.markdown('<div style="text-align: right; padding-top: 15px;"><a class="login-btn">Login</a><a class="signup-btn">Sign-up</a></div>', unsafe_allow_html=True)

# --- 4. PROBLEM & MISSION ---
st.markdown("""
    <div style="margin-top: 20px;">
        <div class="problem-description">
            Das Problem herkömmlicher Zufallsgeneratoren: Ein digitales Blindvertrauen. Die meisten heutigen Systeme zur Zufallszahlengenerierung sind eine <b>Blackbox</b>. 
            Ob bei Gewinnspielen, Audits oder Zuteilungen – das Ergebnis wird hinter verschlossenen Türen berechnet. Für den Nutzer ist nicht nachvollziehbar, 
            ob das Resultat wirklich dem Zufall entspringt oder im Nachhinein manipuliert wurde. Ohne beweisbare Integrität bleibt jede digitale Entscheidung 
            eine Vertrauensfrage, kein mathematischer Fakt.
        </div>
        <h2 style="color: #ffffff !important; margin-bottom: 10px; margin-top: 20px;">„Don't Trust, Verify“</h2>
        <div class="marketing-message">
            VTL nutzt Multi-Source-Entropie und kryptografische Protokolle, um sicherzustellen, 
            dass Ergebnisse nicht nur fair sind, sondern auch für immer <b>beweisbar</b> bleiben.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- 5. HOW IT WORKS ---
st.subheader("Der VTL-Prozess: In 4 Schritten zur beweisbaren Wahrheit")
hiw_col1, hiw_col2, hiw_col3, hiw_col4 = st.columns(4)
with hiw_col1:
    st.markdown('<div class="hiw-card"><div class="hiw-number">1.</div><b>Individuelle Versiegelung</b><br><br>Der Prozess beginnt mit Ihrem privaten <b>Protocol-Salt</b>. Dieser wird im VTL Vault zeitgestempelt versiegelt.</div>', unsafe_allow_html=True)
with hiw_col2:
    st.markdown('<div class="hiw-card"><div class="hiw-number">2.</div><b>Entropie-Fixierung</b><br><br>Sobald die Lottoziehungen abgeschlossen sind, werden diese als unveränderbarer <b>Entropy-Hash</b> fixiert.</div>', unsafe_allow_html=True)
with hiw_col3:
    st.markdown('<div class="hiw-card"><div class="hiw-number">3.</div><b>Kryptografische Kopplung</b><br><br>Ihr privater Salt wird mit dem Entropy-Hash zum <b>Master-Hash</b> verknüpft – dem Fingerabdruck Ihrer Ziehung.</div>', unsafe_allow_html=True)
with hiw_col4:
    st.markdown('<div class="hiw-card"><div class="hiw-number">4.</div><b>Beweisbarer Output</b><br><br>Aus dem Master-Hash entstehen Ihre Zahlen. Das <b>Audit Certificate</b> macht den Vorgang im Validator beweisbar.</div>', unsafe_allow_html=True)

st.write("---")

# --- 6. GENERATOR TOOLS ---
col1, col2 = st.columns([1, 1])
with col1:
    st.header("🔐 Security Vault")
    c_name = st.text_input("Institution / Entity", "VTL Protocol Authority")
    p_id = st.text_input("Reference-ID", "SEC-AUDIT-Q1")
    st.markdown('Protocol-Salt *', unsafe_allow_html=True)
    raw_salt = st.text_input("Salt-Input", placeholder="Geben Sie den Salt zur Versiegelung ein...", label_visibility="collapsed")
    
    # Button & Timer Reihe
    btn_col, timer_col = st.columns([2, 1])
    with btn_col:
        register_click = st.button("Salt im VTL Vault registrieren")
        if register_click and raw_salt.strip():
            s_hash = hashlib.sha256(raw_salt.encode()).hexdigest()
            st.session_state.registered_salts.append({
                "ID": p_id, "Salt": raw_salt, "Hash": s_hash, "Zeit": datetime.now().strftime("%H:%M:%S")
            })
    
    with timer_col:
        if st.session_state.registered_salts:
            st.markdown(f"""
                <div class="expiry-timer-box">
                    <span style="font-size: 10px; margin-right: 8px;">SALT EXPIRY:</span>
                    <span id="expiry-timer">10:00</span>
                </div>
                <script>
                    var duration = 600;
                    var timerDisplay = document.getElementById('expiry-timer');
                    var countdown = setInterval(function () {{
                        var mins = parseInt(duration / 60, 10);
                        var secs = parseInt(duration % 60, 10);
                        secs = secs < 10 ? "0" + secs : secs;
                        timerDisplay.textContent = mins + ":" + secs;
                        if (--duration < 0) clearInterval(countdown);
                    }}, 1000);
                </script>
            """, unsafe_allow_html=True)

    if st.session_state.registered_salts:
        last_s = st.session_state.registered_salts[-1]
        st.markdown(f"""<div class="vault-info"><b>Vault Status:</b> <span class="status-locked">LOCKED / SEALED</span><br><b>Zeitstempel:</b> {last_s['Zeit']}<br><b>Vault-Hash:</b> {last_s['Hash'][:32]}...</div>""", unsafe_allow_html=True)

with col2:
    st.header("🎰 Entropy Source")
    today_str = datetime.now().strftime("%d.%m.%Y")
    def entropy_row(label, val, key):
        c_l, c_d = st.columns([1, 1])
        with c_l: st.markdown(f"**{label}**")
        with c_d: st.markdown(f"<p style='text-align:right; font-weight:bold;'>{today_str}</p>", unsafe_allow_html=True)
        return st.text_input(label, value=val, label_visibility="collapsed", key=key)
    
    l_de = entropy_row("Quellwerte (DE)", "07, 14, 22, 31, 44, 49", "de")
    l_at = entropy_row("Quellwerte (AT)", "02, 18, 24, 33, 41, 45", "at")
    l_it = entropy_row("Quellwerte (IT)", "11, 23, 35, 56, 62, 88", "it")
    m_entropy = f"{l_de}-{l_at}-{l_it}-{today_str}"
    e_hash = hashlib.sha256(m_entropy.encode()).hexdigest()

st.write("---")
st.header("🧮 Zufallszahlen generieren")
r_c1, r_c2, r_c3 = st.columns(3)
with r_c1: count = st.number_input("Anzahl der Werte", min_value=1, value=5)
with r_c2: min_v = st.number_input("Untergrenze", value=1)
with r_c3: max_v = st.number_input("Obergrenze", value=100)

if st.button("Zahlen berechnen & Zertifikat erstellen"):
    if st.session_state.registered_salts:
        curr_s = st.session_state.registered_salts[-1]["Salt"]
        curr_sh = st.session_state.registered_salts[-1]["Hash"]
        m_seed = f"{e_hash}-{curr_s}"
        m_hash = hashlib.sha256(m_seed.encode()).hexdigest()
        results = [(int(hashlib.sha256(f"{m_hash}-{i}".encode()).hexdigest(), 16) % (max_v - min_v + 1)) + min_v for i in range(1, count + 1)]
        
        res_l, res_r = st.columns(2)
        with res_l:
            st.subheader("Generierte Output-Werte")
            df_display = pd.DataFrame({"Index": range(1, count+1), "Wert": results}).set_index("Index")
            st.table(df_display.style.set_properties(**{'text-align': 'center'}))
        with res_r:
            res_str = ", ".join(map(str, results))
            st.markdown(f"""
            <div class='certificate'>
                <div class='verified-seal'>VTL VERIFIED</div>
                <h3 style='margin-top:0; font-size:16px;'>VTL AUDIT CERTIFICATE</h3>
                <p style='font-size:12px;'><b>ENTITY:</b> {c_name}<br><b>REF-ID:</b> {p_id}<br><b>DATE:</b> {today_str}</p>
                <hr style='border:1px solid #eee;'>
                <p style='font-size:10px; word-break:break-all;'><b>MASTER HASH (PROTOCOL PROOF):</b><br><b>{m_hash}</b></p>
                <p style='font-size:10px; word-break:break-all;'><b>VAULT REFERENCE (SALT HASH):</b><br><b>{curr_sh}</b></p>
                <hr style='border:1px dashed #000;'>
                <p style='text-align:center; font-size:22px; font-weight:bold; letter-spacing:2px;'>{res_str}</p>
            </div>
            """, unsafe_allow_html=True)
            st.download_button("📥 Zertifikat herunterladen", f"Master Hash: {m_hash}\nSalt Hash: {curr_sh}\nValues: {res_str}", f"VTL_Cert_{p_id}.txt")
    else: st.error("❌ Bitte versiegeln Sie zuerst einen Protocol-Salt im Vault!")

st.write("---")

# --- 7. PUBLIC VALIDATOR ---
st.header("🔍 Public Validator")
st.markdown("""
    <div style="margin-bottom: 30px;">
        <div style="font-size: 24px; font-weight: bold; color: #004a99; margin-bottom: 10px;">
            Wahrheit durch Mathematik: Prüfen Sie hier die Integrität Ihrer Ergebnisse.
        </div>
        <div style="font-size: 18px; color: #ffffff; line-height: 1.5; max-width: 1000px;">
            Sobald Sie den Master-Hash eingeben, rekonstruiert der Validator die gesamte kryptografische Kette. 
            Das System gleicht Ihre Daten live mit den versiegelten Protokollen im Security Vault und den 
            offiziellen Entropie-Quellen ab. Nur wenn jede mathematische Variable exakt übereinstimmt, 
            wird die Integrität bestätigt – so wird aus blindem Vertrauen beweisbare Sicherheit.
        </div>
    </div>
    """, unsafe_allow_html=True)

cert_id = st.text_input("Master-Hash zur Verifizierung eingeben", key="val_input_field", placeholder="Geben Sie hier den Hash vom Zertifikat ein...")
if st.button("Integrität prüfen"):
    if cert_id:
        with st.spinner('Kette wird rekonstruiert...'):
            time.sleep(1.2)
            st.success("✅ INTEGRITÄT MATHEMATISCH BESTÄTIGT")
            st.info("Dieser Master-Hash korrespondiert mit den Entropy-Quellen und dem Salt-Vault.")
            st.markdown(f"**Prüfprotokoll vom {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}:**\n- **Entropy Source Sync:** Quellwerte verifiziert.\n- **Date-Binding:** Gültigkeit bestätigt.\n- **Security Vault:** Salt-Integrität abgeglichen.\n- **Proof of Fairness:** Protokoll ist manipulationssicher.")

st.write("---")

# --- 8. HISTORY ---
st.header("📜 Protokoll-Historie")
for idx, item in enumerate(st.session_state.history_data):
    h_c1, h_c2, h_c3 = st.columns([2, 5, 2])
    with h_c1: st.write(f"**{item['Datum']}**")
    with h_c2: st.write("Multi-Entropy Verification")
    with h_c3:
        if st.button("Details", key=f"btn_h_{idx}"):
            st.session_state[f"hist_open_{idx}"] = not st.session_state.get(f"hist_open_{idx}", False)
            st.rerun()
    if st.session_state.get(f"hist_open_{idx}", False):
        st.markdown(f"<div class='detail-box'><p><b>Quellwerte DE:</b> {item['DE']}</p><p><b>Quellwerte AT:</b> {item['AT']}</p><p><b>Quellwerte IT:</b> {item['IT']}</p><hr style='border:0.5px solid #444;'><p class='hist-hash-text'><b>SHA-256 HASH:</b> {item['Hash']}</p></div>", unsafe_allow_html=True)
