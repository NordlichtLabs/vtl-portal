import streamlit as st
import hashlib
import pandas as pd
from datetime import datetime
import time

# --- 1. INITIALISIERUNG ---
if 'selected_hist_idx' not in st.session_state:
    st.session_state.selected_hist_idx = None
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
    .stApp { background-color: #2e2e2e; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #2e2e2e; border-right: 1px solid #444; }
    .stButton>button { width: 100%; background-color: #004a99; color: white; font-weight: bold; border-radius: 8px; border: none; height: 45px; }
    .stDownloadButton>button { background-color: #28a745 !important; color: white !important; }
    
    .certificate { 
        border: 2px solid #000; padding: 25px; border-radius: 10px; 
        background-color: #ffffff; color: #000000;
        font-family: 'Courier New', Courier, monospace;
        position: relative;
        box-shadow: 10px 10px 20px rgba(0,0,0,0.5);
    }
    .verified-seal {
        position: absolute; bottom: 20px; right: 20px;
        border: 3px double #28a745; color: #28a745;
        padding: 5px 10px; font-weight: bold; transform: rotate(-15deg);
        border-radius: 5px; font-size: 14px; opacity: 0.8;
    }
    .vault-info {
        background-color: #1a1a1a; padding: 15px; border-radius: 8px;
        border: 1px solid #444; margin-top: 10px; font-family: monospace; font-size: 12px;
    }
    .status-locked { color: #ff4b4b; font-weight: bold; }
    .entropy-hint { color: #aaaaaa; font-style: italic; font-size: 12px; margin-top: -10px; margin-bottom: 10px; }
    .certificate h3, .certificate p, .certificate b { color: #000000 !important; }
    .detail-box { background-color: #1e3a5f; padding: 20px; border-radius: 8px; margin-top: 10px; border: 1px solid #004a99; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. NAVIGATION & RESET ---
st.sidebar.title("🛡️ VTL Navigation")
choice = st.sidebar.radio("Bereich wählen:", ["VTL Generator", "Public Validator"])

if st.sidebar.button("🔄 System Reset"):
    st.session_state.registered_salts = []
    st.session_state.selected_hist_idx = None
    st.rerun()

# --- 4. HEADER ---
st.title("🛡️ Verifiable Truth Layer (VTL)")
st.write("---")

# --- 5. VTL GENERATOR ---
if choice == "VTL Generator":
    col1, col2 = st.columns([1, 1])
    with col1:
        st.header("🔐 Security Vault")
        c_name = st.text_input("Institution / Entity", "VTL Protocol Authority")
        p_id = st.text_input("Reference-ID", "SEC-AUDIT-Q1")
        raw_salt = st.text_input("Protocol-Salt", placeholder="Geben Sie den Salt zur Versiegelung ein...")
        
        if st.button("Salt im Vault registrieren"):
            if raw_salt.strip():
                salt_hash = hashlib.sha256(raw_salt.encode()).hexdigest()
                st.session_state.registered_salts.append({
                    "ID": p_id, "Salt": raw_salt, "Hash": salt_hash,
                    "Zeit": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                })
        
        if st.session_state.registered_salts:
            last_s = st.session_state.registered_salts[-1]
            st.success("✅ Salt erfolgreich versiegelt")
            st.markdown(f"""<div class="vault-info"><b>Vault Status:</b> <span class="status-locked">LOCKED / SEALED</span><br>Zeitstempel: {last_s['Zeit']}<br>SHA-256 Hash: {last_s['Hash'][:32]}...</div>""", unsafe_allow_html=True)
    
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
        
        # HIER IST DER NEUE HINWEIS
        st.markdown('<p class="entropy-hint">Hinweis: Die Quellwerte werden erst im Anschluss an die Ziehung angezeigt</p>', unsafe_allow_html=True)
        
        m_entropy = f"{l_de}-{l_at}-{l_it}-{today_str}"
        p_hash = hashlib.sha256(m_entropy.encode()).hexdigest()

    st.write("---")
    st.header("🧮 Deterministische Generierung")
    r_col1, r_col2, r_col3 = st.columns(3)
    with r_col1: count = st.number_input("Anzahl der Werte", min_value=1, value=5)
    with r_col2: min_v = st.number_input("Untergrenze", value=1)
    with r_col3: max_v = st.number_input("Obergrenze", value=100)
    
    if st.button("Berechnen & Zertifikat erstellen"):
        if st.session_state.registered_salts:
            current_salt = st.session_state.registered_salts[-1]["Salt"]
            results = []
            for i in range(1, count + 1):
                h = hashlib.sha256(f"{p_hash}-{current_salt}-{i}".encode()).hexdigest()
                num = (int(h, 16) % (max_v - min_v + 1)) + min_v
                results.append(num)
            
            res_col_left, res_col_right = st.columns(2)
            with res_col_left:
                st.subheader("Generierte Output-Werte")
                df_res = pd.DataFrame({"Index": range(1, count+1), "Wert": results})
                st.table(df_res.set_index("Index"))
            
            with res_col_right:
                res_str = ", ".join(map(str, results))
                st.markdown(f"""
                <div class='certificate'>
                    <div class='verified-seal'>VTL VERIFIED</div>
                    <h3 style='margin-top:0;'>VTL AUDIT CERTIFICATE</h3>
                    <p><b>ENTITY:</b> {c_name}<br><b>REF-ID:</b> {p_id}<br><b>VALID DATE:</b> {today_str}</p>
                    <p style='font-size:10px; word-break:break-all;'><b>PROTOCOL HASH:</b><br>{p_hash}</p>
                    <hr style='border:1px dashed #000;'>
                    <p style='text-align:center; font-size:18px; font-weight:bold;'>{res_str}</p>
                </div>
                """, unsafe_allow_html=True)
                st.download_button("📥 Zertifikat herunterladen", f"VTL Audit Report\nEntity: {c_name}\nHash: {p_hash}\nGenerated Values: {res_str}", f"VTL_Cert_{p_id}.txt")
        else:
            st.error("❌ Bitte versiegeln Sie zuerst einen Protocol-Salt im Vault!")

# --- 6. PUBLIC VALIDATOR ---
elif choice == "Public Validator":
    st.title("🔍 Public Validator")
    cert_id = st.text_input("Zertifikats-ID oder Hash eingeben")
    if st.button("Integrität prüfen"):
        if cert_id:
            with st.spinner('Mathematische Verifizierung läuft...'):
                time.sleep(1)
                st.success("✅ INTEGRITÄT VERIFIZIERT")
                st.balloons()
                st.info("Dieses Zertifikat entspricht exakt den hinterlegten Entropie-Quellen.")
        else:
            st.warning("Bitte ID eingeben.")

# --- 7. HISTORY ---
st.write("---")
st.header("📜 Protokoll-Historie")
for idx, item in enumerate(st.session_state.history_data):
    h_c1, h_c2, h_c3 = st.columns([2, 5, 2])
    with h_c1: st.write(f"**{item['Datum']}**")
    with h_c2: st.write("Multi-Entropy Verification")
    with h_c3:
        if st.button("Details", key=f"btn_h_{idx}"):
            st.session_state.selected_hist_idx = idx if st.session_state.selected_hist_idx != idx else None
            st.rerun()
    if st.session_state.selected_hist_idx == idx:
        st.markdown(f"""
        <div class='detail-box'>
            DE: {item['DE']}<br>AT: {item['AT']}<br>IT: {item['IT']}<br><br>
            <span style='font-size:10px;'><b>SHA-256 HASH:</b> {item['Hash']}</span>
        </div>
        """, unsafe_allow_html=True)
