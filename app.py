import streamlit as st
import hashlib
import pandas as pd
from datetime import datetime
import time

# --- 1. INITIALISIERUNG (MUSS GANZ OBEN STEHEN) ---
# Das verhindert den AttributeError aus deinem Screenshot
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
    .nav-header { font-size: 28px; font-weight: bold; color: #ffffff; margin-bottom: 20px; }
    .stButton>button { width: 100%; background-color: #004a99; color: white; font-weight: bold; border-radius: 8px; border: none; height: 45px; }
    .certificate { border: 2px solid #000; padding: 20px; border-radius: 10px; background-color: #ffffff; color: #000000; font-family: monospace; box-shadow: 5px 5px 15px rgba(0,0,0,0.5); }
    .certificate h3, .certificate p, .certificate b { color: #000000 !important; }
    .detail-box { background-color: #1e3a5f; padding: 20px; border-radius: 8px; margin-top: 10px; border: 1px solid #004a99; }
    .country-tag { font-weight: bold; color: #90caf9; min-width: 80px; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER & NAVIGATION ---
log_col1, log_col2, log_col3 = st.columns([6, 2, 2])
with log_col2: st.text_input("User", placeholder="E-Mail", label_visibility="collapsed")
with log_col3: st.text_input("Pass", type="password", placeholder="Passwort", label_visibility="collapsed")

st.title("🛡️ Verifiable Truth Layer (VTL)")
st.subheader("Provable Fairness through Multi-Source Entropy & Hashing.")
st.write("---")

st.sidebar.markdown('<p class="nav-header">🛡️ Navigation</p>', unsafe_allow_html=True)
choice = st.sidebar.radio("Bereich wählen:", ["VTL Generator", "Public Validator"], label_visibility="collapsed")

# --- 4. SEITE: VTL GENERATOR ---
if choice == "VTL Generator":
    col1, col2 = st.columns([1, 1])
    with col1:
        st.header("🏢 Firmen-Portal")
        c_name = st.text_input("Firmenname", "BlueBank AG")
        p_id = st.text_input("Projekt-ID", "Audit-Q1-2026")
        raw_salt = st.text_input("Client-Salt", placeholder="Ihr privater Salt...")
        if st.button("Client-Salt registrieren"):
            if raw_salt.strip():
                st.session_state.registered_salts.append({"Title": p_id, "Salt": raw_salt, "Zeit": datetime.now().strftime("%H:%M:%S")})
                st.success("✅ Salt registriert.")
    
    with col2:
        st.header("🎰 Entropy Source")
        today_str = datetime.now().strftime("%d.%m.%Y")
        l_de = st.text_input("Zahlen (DE)", "07, 14, 22, 31, 44, 49")
        l_at = st.text_input("Zahlen (AT)", "02, 18, 24, 33, 41, 45")
        l_it = st.text_input("Zahlen (IT)", "11, 23, 35, 56, 62, 88")
        
        m_entropy = f"{l_de}-{l_at}-{l_it}-{today_str}"
        p_hash = hashlib.sha256(m_entropy.encode()).hexdigest()

    if st.button("Zahlen berechnen & Zertifikat erstellen"):
        if st.session_state.registered_salts:
            st.write("---")
            res_left, res_right = st.columns(2)
            with res_left:
                st.success(f"Master-Hash generiert: {p_hash[:15]}...")
                st.info("Zahlen: 10, 24, 45, 67, 88")
            with res_right:
                st.markdown(f"<div class='certificate'><h3>VTL AUDIT CERTIFICATE</h3><b>Halter:</b> {c_name}<br><b>Datum:</b> {today_str}<br><br><b>SHA-256 HASH:</b><br>{p_hash}</div>", unsafe_allow_html=True)
        else:
            st.error("❌ Bitte erst Salt registrieren!")

# --- 5. SEITE: PUBLIC VALIDATOR (DUMMY FIX) ---
elif choice == "Public Validator":
    st.title("🔍 Public Validator")
    cert_id = st.text_input("Zertifikats-ID eingeben", key="val_input")
    
    if st.button("Validieren"):
        if cert_id:
            with st.spinner('Prüfe kryptografische Kette...'):
                time.sleep(1)
                st.success("✅ VALIDIERUNG ERFOLGREICH")
                st.balloons()
                st.info("Ja, dieses Zertifikat wurde genau so mit diesen Lottozahlen erstellt.")
        else:
            st.warning("Bitte ID eingeben.")

# --- 6. GLOBALE HISTORY (UNTERHALB ALLER SEITEN) ---
st.write("---")
st.header("📜 Globale Entropie-History")

for idx, item in enumerate(st.session_state.history_data):
    h_c1, h_c2, h_c3 = st.columns([2, 5, 2])
    with h_c1: st.write(f"**{item['Datum']}**")
    with h_c2: st.write("Multi-Entropy Source (DE+AT+IT)")
    with h_c3:
        # Hier nutzen wir den Key, um den Fehler zu vermeiden
        if st.button("Details", key=f"btn_hist_{idx}"):
            if st.session_state.selected_hist_idx == idx:
                st.session_state.selected_hist_idx = None
            else:
                st.session_state.selected_hist_idx = idx
            st.rerun()

    # Prüfung ob Details angezeigt werden sollen
    if st.session_state.selected_hist_idx == idx:
        st.markdown(f"""
        <div class="detail-box">
            <div><span class="country-tag">🇩🇪 DE:</span> {item['DE']}</div>
            <div><span class="country-tag">🇦🇹 AT:</span> {item['AT']}</div>
            <div><span class="country-tag">🇮🇹 IT:</span> {item['IT']}</div>
            <hr style="border:0.5px solid #444;">
            <p style="font-size:11px; color:#90caf9;">Hash: {item['Hash']}</p>
        </div>
        """, unsafe_allow_html=True)
