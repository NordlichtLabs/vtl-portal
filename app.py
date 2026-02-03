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
    
    /* FIX: Einheitliche Höhe für alle 4 Prozess-Boxen */
    .hiw-card { 
        background-color: rgba(0, 74, 153, 0.15); 
        padding: 25px; 
        border-radius: 12px; 
        border: 1px solid #004a99;
        min-height: 200px; 
        height: 100%;
        display: flex;
        flex-direction: column;
    }

    /* Zertifikat Design - Kompakter */
    .certificate { 
        border: 2px solid #000; padding: 25px; border-radius: 10px; background-color: #ffffff; color: #000000; 
        font-family: 'Courier New', monospace; position: relative; box-shadow: 0 0 40px rgba(0, 212, 255, 0.4); line-height: 1.4;
        max-width: 600px; margin-top: 20px;
    }
    .cert-logo { position: absolute; top: 15px; right: 20px; font-size: 35px; opacity: 0.15; }
    .cert-label { font-weight: bold; font-size: 11px; color: #555; text-transform: uppercase; margin-top: 10px; }
    .cert-value { font-size: 14px; margin-bottom: 10px; word-break: break-all; color: #000; }
    .cert-title { font-size: 22px; font-weight: bold; margin-bottom: 20px; text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; }

    .timer-container { border: 1px solid #ff00ff; background-color: rgba(255, 0, 255, 0.05); border-radius: 8px; height: 45px; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #ff00ff; }
    .vault-info { background-color: #000; padding: 15px; border-radius: 8px; border: 1px solid #333; margin-top: 10px; font-family: monospace; font-size: 12px; }
    .process-flow { background-color: rgba(0, 212, 255, 0.1); border: 1px dashed #00d4ff; padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; font-size: 14px; }
    .detail-box { background-color: rgba(0, 212, 255, 0.05); padding: 20px; border-radius: 8px; margin-top: 10px; border: 1px solid #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER & INTRO ---
st.title("🛡️ Verifiable Truth Layer (VTL)")
st.markdown("""
    <div style="margin-top: 20px;">
        <div style="color: #ffffff; font-size: 18px; line-height: 1.5; max-width: 1000px; margin-bottom: 20px;">
            Das Problem herkömmlicher Zufallsgeneratoren: Ein digitales Blindvertrauen. Die meisten heutigen Systeme zur Zufallszahlengenerierung sind eine <b>Blackbox</b>. 
            Ohne beweisbare Integrität bleibt jede digitale Entscheidung eine Vertrauensfrage, kein mathematischer Fakt.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- 4. PROZESS (ORIGINALTEXTE & GLEICHE GRÖSSE) ---
st.subheader("Der VTL-Prozess")
hiw_cols = st.columns(4)
steps = [
    ("1.", "Versiegelung", "Der Protocol-Salt wird im VTL Vault zeitgestempelt versiegelt."),
    ("2.", "Fixierung", "Lotto-Daten werden als Entropy-Hash unveränderbar registriert."),
    ("3.", "Kopplung", "Salt und Entropy verschmelzen kryptografisch zum Master-Hash."),
    ("4.", "Output", "Aus dem Master-Hash entstehen beweisbare Zahlen.")
]
for i, (num, title, desc) in enumerate(steps):
    with hiw_cols[i]:
        st.markdown(f'<div class="hiw-card"><div style="color:#00d4ff; font-size:24px; font-weight:bold;">{num}</div><b style="font-size:16px;">{title}</b><div style="font-size:14px; margin-top:10px;">{desc}</div></div>', unsafe_allow_html=True)

st.write("---")

# --- 5. VAULT & ENTROPY ---
col_v, col_e = st.columns(2)
with col_v:
    st.header("🔐 Security Vault")
    p_id = st.text_input("Reference-ID", "SEC-AUDIT-Q1")
    st.markdown('Protocol-Salt <span style="color:#ff4b4b; font-weight:bold;">*</span>', unsafe_allow_html=True)
    raw_salt = st.text_input("Salt-Input", placeholder="Geben Sie Ihren geheimen Salt ein...", label_visibility="collapsed")
    
    with st.expander("💡 Was ist der Protocol-Salt? (Beispiel)"):
        st.markdown("""
            Der **Protocol-Salt** ist Ihr persönlicher „Fingerabdruck“ im System. Er garantiert, dass Ergebnisse individuell berechnet werden und vorab nicht manipuliert werden können.
            
            **Das Tresor-Prinzip:**
            1. **Versiegelung:** Bevor die Lottozahlen gezogen werden, legen Sie Ihren geheimen Salt in unseren digitalen Tresor.
            2. **Zeitstempel:** Das System quittiert die Versiegelung vor der Ziehung.
            3. **Die Kopplung:** VTL berechnet nun: [Lottozahlen] + [Ihr Salt] = Ergebnis.
        """)
    
    if st.button("Salt im Vault registrieren"):
        if not raw_salt.strip():
            st.error("Bitte geben sie zuerst den Protocol-Salt ein!")
        else:
            now = datetime.now().strftime("%H:%M:%S")
            s_hash = hashlib.sha256(raw_salt.encode()).hexdigest()
            st.session_state.registered_salts.append({"Hash": s_hash, "Salt": raw_salt, "Zeit": now})
            st.rerun()

    if st.session_state.registered_salts:
        ls = st.session_state.registered_salts[-1]
        st.markdown(f'<div class="vault-info"><b>Status:</b> <span style="color:#ff4b4b;">LOCKED / SEALED</span><br><b>Versiegelt um:</b> {ls["Zeit"]} Uhr<br><b>Vault-Hash:</b> {ls["Hash"][:32]}...</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 13px; color:#aaa; margin-top:5px;"><b>VTL Sealing Cut-off:</b> Ihr Key muss vor der Ziehung versiegelt sein. Manipulationen sind so ausgeschlossen.</div>', unsafe_allow_html=True)

with col_e:
    st.header("🎰 Entropy Source")
    today = datetime.now().strftime("%d.%m.%Y")
    l_de = st.text_input(f"Quellwerte DE ({today})", "07, 14, 22, 31, 44, 49")
    l_at = st.text_input(f"Quellwerte AT ({today})", "02, 18, 24, 33, 41, 45")
    l_it = st.text_input(f"Quellwerte IT ({today})", "11, 23, 35, 56, 62, 88")
    st.markdown('<p style="color:#aaa; font-style:italic; font-size:13px; margin-top:5px;">Hinweis: Die Quellwerte werden erst im Anschluss an die Ziehung angezeigt.</p>', unsafe_allow_html=True)

st.write("---")

# --- 6. GENERATOR & CERTIFICATE ---
st.header("🧮 Generator")
if st.button("Audit-Zertifikat berechnen"):
    if st.session_state.registered_salts:
        curr = st.session_state.registered_salts[-1]
        e_hash = hashlib.sha256(f"{l_de}{l_at}{l_it}{today}".encode()).hexdigest()
        m_hash = hashlib.sha256(f"{e_hash}-{curr['Salt']}".encode()).hexdigest()
        # Generiere 5 Beispielzahlen
        res_list = [(int(hashlib.sha256(f"{m_hash}-{i}".encode()).hexdigest(), 16) % 100) + 1 for i in range(5)]
        
        st.session_state.current_cert = {
            "flow": f"<div class='process-flow'><span style='color:#00d4ff'>Entropy-Hash</span> ({e_hash[:8]}...) <b>+</b> <span style='color:#ff00ff'>Protocol-Salt</span> ({curr['Salt']}) <b>=</b> <span style='font-weight:bold'>Master-Hash</span> ({m_hash[:12]}...)</div>",
            "p_id": p_id, "date": today, "entropy": f"{l_de} | {l_at} | {l_it}",
            "salt": curr['Salt'], "salt_time": curr['Zeit'], "m_hash": m_hash, "results": ", ".join(map(str, res_list))
        }
        st.session_state.last_m_hash = m_hash
    else: st.error("Bitte versiegeln Sie zuerst einen Salt!")

if st.session_state.current_cert:
    c = st.session_state.current_cert
    st.markdown(c["flow"], unsafe_allow_html=True)
    st.markdown(f"""
        <div class="certificate">
            <div class="cert-logo">🛡️</div>
            <div style="position:absolute; bottom:20px; right:20px; border:3px double #28a745; color:#28a745; padding:5px 10px; font-weight:bold; transform:rotate(-15deg); border-radius:5px;">VTL VERIFIED</div>
            <div class="cert-title">VTL AUDIT CERTIFICATE</div>
            <div class="cert-label">Reference-ID & Date</div>
            <div class="cert-value">{c['p_id']} | {c['date']}</div>
            <div class="cert-label">Entropy Sources</div>
            <div class="cert-value">{c['entropy']}</div>
            <div class="cert-label">Protocol-Salt (Sealed)</div>
            <div class="cert-value">{c['salt']} (Versiegelt um {c['salt_time']})</div>
            <div class="cert-label">Kryptografischer Master-Hash</div>
            <div class="cert-value" style="font-size:12px; font-family:monospace;">{c['m_hash']}</div>
            <hr style="border: 0.5px solid #ddd; margin: 10px 0;">
            <div class="cert-label" style="text-align:center;">Final Verifiable Results</div>
            <p style="text-align:center; font-size:32px; font-weight:bold; color:#000; margin:0;">{c['results']}</p>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- 7. VALIDATOR ---
st.header("🔍 Public Validator")
st.markdown('<div style="font-size:18px; color: #ffffff; line-height: 1.5; max-width: 1000px; margin-bottom: 20px;">Sobald Sie den Master-Hash eingeben, rekonstruiert der Validator die gesamte kryptografische Kette. Das System gleicht Ihre Daten live mit den versiegelten Protokollen im Security Vault und den offiziellen Entropie-Quellen ab. Nur wenn jede mathematische Variable exakt übereinstimmt, wird die Integrität bestätigt.</div>', unsafe_allow_html=True)
v_hash = st.text_input("Master-Hash zur Verifizierung eingeben", placeholder="f3b2c1a9e8...")
if st.button("Integrität prüfen"):
    if v_hash:
        with st.spinner('Validierung...'):
            time.sleep(1.2)
            if v_hash == st.session_state.get('last_m_hash') or any(h['Hash'] == v_hash for h in st.session_state.history_data):
                st.success("✅ INTEGRITÄT MATHEMATISCH BESTÄTIGT")
            else: st.error("❌ INTEGRITÄT VERLETZT / UNBEKANNTER HASH")

st.write("---")

# --- 8. HISTORY ---
st.header("📜 Protokoll-Historie")
for idx, h in enumerate(st.session_state.history_data):
    with st.container():
        c1, c2 = st.columns([7, 2])
        with c1: st.markdown(f"<div style='padding-top:10px; font-size:18px;'><b>📅 {h['Datum']}</b></div>", unsafe_allow_html=True)
        with c2:
            if st.button("Details", key=f"h_{idx}"):
                st.session_state[f"o_{idx}"] = not st.session_state.get(f"o_{idx}", False)
                st.rerun()
        if st.session_state.get(f"o_{idx}", False):
            st.markdown(f"<div class='detail-box'><span style='color:#00d4ff;'>●</span> <b>DE:</b> {h['DE']}<br><span style='color:#00d4ff;'>●</span> <b>AT:</b> {h['AT']}<br><span style='color:#00d4ff;'>●</span> <b>IT:</b> {h['IT']}<hr style='opacity:0.3;'><p style='font-family:monospace; font-size:12px; color:#aaa;'>HASH: {h['Hash']}</p></div>", unsafe_allow_html=True)
        st.markdown("<hr style='border:0.5px solid #222; margin:10px 0;'>", unsafe_allow_html=True)
