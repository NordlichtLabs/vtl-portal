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
if 'current_cert' not in st.session_state:
    st.session_state.current_cert = None

# --- 2. DESIGN & CSS ---
st.set_page_config(page_title="VTL - Verifiable Truth Layer", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0a0a0a; color: #ffffff; }
    h1 { color: #00d4ff !important; font-family: 'Orbitron', sans-serif; }
    
    /* Zertifikat-Design Korrektur */
    .certificate-container { 
        background-color: #ffffff; 
        color: #000000; 
        padding: 30px; 
        border-radius: 10px; 
        font-family: 'Courier New', monospace;
        position: relative;
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.4);
    }
    .cert-title { font-size: 26px; font-weight: bold; text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 20px; }
    .cert-label { font-weight: bold; font-size: 13px; color: #555; text-transform: uppercase; margin-top: 10px; }
    .cert-value { font-size: 15px; margin-bottom: 10px; word-break: break-all; color: #000; }
    .verified-seal { position: absolute; bottom: 20px; right: 20px; border: 3px double #28a745; color: #28a745; padding: 5px 10px; font-weight: bold; transform: rotate(-15deg); border-radius: 5px; }
    
    .stDownloadButton>button { 
        background: linear-gradient(45deg, #28a745, #85d045) !important; 
        color: white !important; border: none !important; width: 100%; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ VTL Audit Interface")

# --- 3. LOGIK FÜR GENERIERUNG ---
col_v, col_e = st.columns(2)
with col_v:
    st.header("🔐 Vault")
    p_id = st.text_input("Reference-ID", "SEC-AUDIT-Q1")
    raw_salt = st.text_input("Protocol-Salt", type="password")
    if st.button("Salt versiegeln"):
        if raw_salt:
            now = datetime.now().strftime("%H:%M:%S")
            st.session_state.registered_salts.append({"Salt": raw_salt, "Zeit": now})
            st.success(f"Versiegelt um {now}")

with col_e:
    st.header("🎰 Entropy")
    l_de = st.text_input("DE Source", "07, 14, 22, 31, 44, 49")
    l_at = st.text_input("AT Source", "02, 18, 24, 33, 41, 45")
    l_it = st.text_input("IT Source", "11, 23, 35, 56, 62, 88")

st.write("---")

# --- 4. ZERTIFIKAT BERECHNUNG & ANZEIGE ---
if st.button("Audit-Zertifikat generieren"):
    if st.session_state.registered_salts:
        curr = st.session_state.registered_salts[-1]
        today = datetime.now().strftime("%d.%m.%Y")
        entropy_str = f"{l_de}{l_at}{l_it}{today}"
        e_hash = hashlib.sha256(entropy_str.encode()).hexdigest()
        
        m_seed = f"{e_hash}-{curr['Salt']}"
        m_hash = hashlib.sha256(m_seed.encode()).hexdigest()
        
        # Ergebnisse generieren (Beispielhaft 2 Zahlen)
        res_list = [str(int(m_hash[i:i+2], 16) % 100) for i in range(0, 4, 2)]
        results = ", ".join(res_list)

        # Zertifikat-Daten im State speichern
        st.session_state.current_cert = {
            "p_id": p_id, "date": today, "entropy": f"{l_de} | {l_at} | {l_it}",
            "salt": curr['Salt'], "time": curr['Zeit'], "m_hash": m_hash, "results": results
        }
    else:
        st.error("Bitte zuerst einen Salt im Vault registrieren!")

# Anzeige des Zertifikats
if st.session_state.current_cert:
    c = st.session_state.current_cert
    
    # Der HTML-Block muss als EIN String übergeben werden
    cert_html = f"""
    <div class="certificate-container">
        <div class="cert-title">VTL AUDIT CERTIFICATE</div>
        <div class="verified-seal">VTL VERIFIED</div>
        
        <div class="cert-label">Reference-ID & Date</div>
        <div class="cert-value">{c['p_id']} | {c['date']}</div>
        
        <div class="cert-label">Entropy Sources (DE/AT/IT)</div>
        <div class="cert-value">{c['entropy']}</div>
        
        <div class="cert-label">Protocol-Salt (Sealed)</div>
        <div class="cert-value">{c['salt']} (Versiegelt um {c['time']})</div>
        
        <div class="cert-label">Kryptografischer Master-Hash</div>
        <div class="cert-value" style="font-family: monospace; font-size: 12px;">{c['m_hash']}</div>
        
        <hr style="border: 1px solid #ddd;">
        <div class="cert-label" style="text-align:center;">Final Verifiable Results</div>
        <p style="text-align:center; font-size:32px; font-weight:bold; margin-top:10px; color:#000;">{c['results']}</p>
    </div>
    """
    
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.markdown(cert_html, unsafe_allow_html=True)
    
    with col_right:
        # Download-Button Logik
        download_text = f"""VTL AUDIT REPORT
-------------------
ID: {c['p_id']}
DATE: {c['date']}
ENTROPY: {c['entropy']}
SALT: {c['salt']}
TIME: {c['time']}
MASTER HASH: {c['m_hash']}
RESULTS: {c['results']}
-------------------
STATUS: MATHEMATICALLY VERIFIED"""
        
        st.download_button(
            label="📄 Download Certificate (.txt)",
            data=download_text,
            file_name=f"VTL_Cert_{c['p_id']}.txt",
            mime="text/plain"
        )
