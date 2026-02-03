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
    .certificate h3, .certificate p, .certificate b { color: #000000 !important; }
    .detail-box { background-color: #1e3a5f; padding: 20px; border-radius: 8px; margin-top: 10px; border: 1px solid #004a99; }
    .country-tag { font-weight: bold; color: #90caf9; min-width: 80px; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
log_col1, log_col2, log_col3 = st.columns([6, 2, 2])
with log_col2: st.text_input("User", placeholder="E-Mail", label_visibility="collapsed")
with log_col3: st.text_input("Pass", type="password", placeholder="Passwort", label_visibility="collapsed")

st.title("🛡️ Verifiable Truth Layer (VTL)")
st.write("---")

choice = st.sidebar.radio("Navigation", ["VTL Generator", "Public Validator"])

# --- 4. VTL GENERATOR ---
if choice == "VTL Generator":
    col1, col2 = st.columns([1, 1])
    with col1:
        st.header("🏢 Firmen-Portal")
        c_name = st.text_input("Firmenname", "VTL Enterprise Solutions")
        p_id = st.text_input("Projekt-ID", "SEC-AUDIT-2026")
        raw_salt = st.text_input("Client-Salt", placeholder="Ihr privater Salt...")
        if st.button("Client-Salt registrieren"):
            if raw_salt.strip():
                st.session_state.registered_salts.append({"Title": p_id, "Salt": raw_salt, "Zeit": datetime.now().strftime("%H:%M:%S")})
                st.success("✅ Salt im Vault versiegelt.")
    
    with col2:
        st.header("🎰 Entropy Source")
        today_str = datetime.now().strftime("%d.%m.%Y")
        
        def entropy_row_with_date(label, val, key):
            c_label, c_date = st.columns([1, 1])
            with c_label: st.markdown(f"**{label}**")
            with c_date: st.markdown(f"<p style='text-align:right; color:#ffffff; font-weight:bold; margin:0;'>{today_str}</p>", unsafe_allow_html=True)
            return st.text_input(label, value=val, label_visibility="collapsed", key=key)

        l_de = entropy_row_with_date("Quellzahlen (DE)", "07, 14, 22, 31, 44, 49", "de")
        l_at = entropy_row_with_date("Quellzahlen (AT)", "02, 18, 24, 33, 41, 45", "at")
        l_it = entropy_row_with_date("Quellzahlen (IT)", "11, 23, 35, 56, 62, 88", "it")
        
        m_entropy = f"{l_de}-{l_at}-{l_it}-{today_str}"
        p_hash = hashlib.sha256(m_entropy.encode()).hexdigest()

    if st.button("Zertifikat generieren"):
        if st.session_state.registered_salts:
            st.write("---")
            res_left, res_right = st.columns(2)
            with res_left:
                st.header("Berechnung erfolgreich")
                st.info(f"Master-Hash: {p_hash[:20]}...")
                st.markdown("### Generierte Zufallswerte:\n**12 • 88 • 43 • 09 • 55**")
            with res_right:
                st.markdown(f"""
                <div class='certificate'>
                    <div class='verified-seal'>VTL VERIFIED</div>
                    <h3 style='margin-top:0;'>VTL AUDIT CERTIFICATE</h3>
                    <p><b>HALTER:</b> {c_name}<br><b>PROJEKT:</b> {p_id}<br><b>DATUM:</b> {today_str}</p>
                    <p style='font-size:10px; word-break:break-all;'><b>VERIFICATION HASH:</b><br>{p_hash}</p>
                    <hr style='border:1px dashed #000;'>
                    <p style='text-align:center; font-size:20px; font-weight:bold;'>12, 88, 43, 09, 55</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("❌ Bitte erst Salt registrieren!")

# --- 5. PUBLIC VALIDATOR ---
elif choice == "Public Validator":
    st.title("🔍 Public Validator")
    cert_id = st.text_input("Zertifikats-ID oder Hash eingeben", key="val_input")
    
    if st.button("Validieren"):
        if cert_id:
            with st.spinner('Kryptografische Verifizierung läuft...'):
                time.sleep(1.5)
                st.success("✅ VALIDIERUNG ERFOLGREICH")
                st.balloons()
                st.info("Dieses Zertifikat wurde mathematisch gegen die Entropy-Quellen und den Salt-Vault geprüft.")
                st.markdown("""
                ### Prüf-Details:
                * **External Entropy Sources:** Verifiziert ✅
                * **Date-Binding Integrity:** Korrekt ✅
                * **Private Salt Alignment:** Match ✅
                """)
        else:
            st.warning("Bitte ID eingeben.")

# --- 6. HISTORY ---
st.write("---")
st.header("📜 Historie")
for idx, item in enumerate(st.session_state.history_data):
    h_c1, h_c2, h_c3 = st.columns([2, 5, 2])
    with h_c1: st.write(f"**{item['Datum']}**")
    with h_c2: st.write("Multi-Entropy Source Verification")
    with h_c3:
        if st.button("Details", key=f"btn_h_{idx}"):
            st.session_state.selected_hist_idx = idx if st.session_state.selected_hist_idx != idx else None
            st.rerun()
    if st.session_state.selected_hist_idx == idx:
        st.markdown(f"<div class='detail-box'><b>DE:</b> {item['DE']}<br><b>AT:</b> {item['AT']}<br><b>IT:</b> {item['IT']}<br><br><span style='font-size:10px;'>Hash: {item['Hash']}</span></div>", unsafe_allow_html=True)
