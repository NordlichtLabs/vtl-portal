import hashlib
import time
from datetime import datetime
import pandas as pd
import streamlit as st

# PDF-Bibliothek sicher importieren
try:
    from fpdf import FPDF
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# --- 1. INITIALISIERUNG ---
if 'registered_salts' not in st.session_state:
    st.session_state.registered_salts = []
if 'current_cert' not in st.session_state:
    st.session_state.current_cert = None

# --- 2. CSS DESIGN ---
st.set_page_config(page_title="VTL - Verifiable Truth Layer", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #0a0a0a; color: #ffffff; }
    h1 { color: #00d4ff !important; font-family: 'Orbitron', sans-serif; }
    
    /* Einheitliche Prozess-Karten Fix */
    .hiw-card { 
        background-color: rgba(0, 74, 153, 0.15); 
        padding: 20px; border-radius: 12px; border: 1px solid #004a99;
        height: 200px; display: flex; flex-direction: column; justify-content: flex-start;
    }

    /* Zertifikat Design Fix (Kompakter & Render-Ready) */
    .certificate-box { 
        border: 2px solid #000; padding: 25px; border-radius: 10px; 
        background-color: #ffffff; color: #000000; font-family: 'Courier New', monospace; 
        position: relative; box-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
        max-width: 600px; margin: auto; line-height: 1.3;
    }
    .cert-label { font-weight: bold; font-size: 11px; color: #555; text-transform: uppercase; margin-top: 8px; }
    .cert-value { font-size: 13px; margin-bottom: 8px; word-break: break-all; color: #000; }
    .cert-title { font-size: 20px; font-weight: bold; text-align: center; border-bottom: 2px solid #000; padding-bottom: 5px; margin-bottom: 15px; }
    .verified-seal { position: absolute; bottom: 15px; right: 15px; border: 2px double #28a745; color: #28a745; padding: 4px 8px; font-weight: bold; transform: rotate(-15deg); border-radius: 5px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Verifiable Truth Layer (VTL)")

# --- 3. PROZESS (ORIGINALTEXTE & GLEICHE GRÖSSE) ---
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

# --- 4. VAULT & ENTROPY ---
col_v, col_e = st.columns(2)
with col_v:
    st.header("🔐 Security Vault")
    raw_salt = st.text_input("Protocol-Salt", placeholder="Geben Sie Ihren geheimen Salt ein...")
    if st.button("Salt im Vault registrieren"):
        if raw_salt:
            now = datetime.now().strftime("%H:%M:%S")
            st.session_state.registered_salts.append({"Salt": raw_salt, "Zeit": now})
            st.rerun()
    if st.session_state.registered_salts:
        ls = st.session_state.registered_salts[-1]
        st.info(f"Status: SEALED | Versiegelt um: {ls['Zeit']}")

with col_e:
    st.header("🎰 Entropy Source")
    l_de = st.text_input("Werte DE", "07, 14, 22, 31, 44, 49")
    l_at = st.text_input("Werte AT", "02, 18, 24, 33, 41, 45")
    l_it = st.text_input("Werte IT", "11, 23, 35, 56, 62, 88")

# --- 5. GENERATOR & PDF LOGIK ---
if st.button("Audit-Zertifikat berechnen"):
    if st.session_state.registered_salts:
        curr = st.session_state.registered_salts[-1]
        today = datetime.now().strftime("%d.%m.%Y")
        e_hash = hashlib.sha256(f"{l_de}{l_at}{l_it}{today}".encode()).hexdigest()
        m_hash = hashlib.sha256(f"{e_hash}-{curr['Salt']}".encode()).hexdigest()
        results = [str(int(m_hash[i:i+2], 16) % 100) for i in range(0, 10, 2)]
        
        st.session_state.current_cert = {
            "p_id": "SEC-AUDIT-Q1", "date": today, "entropy": f"{l_de} | {l_at} | {l_it}",
            "salt": curr['Salt'], "salt_time": curr['Zeit'], "m_hash": m_hash, "results": ", ".join(results)
        }
    else:
        st.error("Bitte zuerst einen Salt registrieren!")

if st.session_state.current_cert:
    c = st.session_state.current_cert
    # HTML-Rendering Fix: Als ein zusammenhängender Block
    cert_html = f"""
    <div class="certificate-box">
        <div class="cert-title">VTL AUDIT CERTIFICATE</div>
        <div class="verified-seal">VTL VERIFIED</div>
        <div class="cert-label">Reference-ID & Date</div>
        <div class="cert-value">{c['p_id']} | {c['date']}</div>
        <div class="cert-label">Entropy Sources</div>
        <div class="cert-value">{c['entropy']}</div>
        <div class="cert-label">Protocol-Salt (Sealed)</div>
        <div class="cert-value">{c['salt']} (Zeit: {c['salt_time']})</div>
        <div class="cert-label">Master-Hash</div>
        <div class="cert-value" style="font-size:10px; font-family:monospace;">{c['m_hash']}</div>
        <hr style="border: 0.5px solid #ddd; margin: 10px 0;">
        <div class="cert-label" style="text-align:center;">Final Verifiable Results</div>
        <p style="text-align:center; font-size:26px; font-weight:bold; color:#000; margin:0;">{c['results']}</p>
    </div>
    """
    st.markdown(cert_html, unsafe_allow_html=True)
    
    # PDF Download Button
    if PDF_SUPPORT:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="VTL AUDIT CERTIFICATE", ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"ID: {c['p_id']} | Date: {c['date']}", ln=True)
        pdf.cell(200, 10, txt=f"Results: {c['results']}", ln=True)
        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button(label="📥 Download Certificate (PDF)", data=pdf_output, file_name="VTL_Audit.pdf", mime="application/pdf")
    else:
        st.warning("Hinweis: Installiere 'fpdf' (pip install fpdf), um den PDF-Download zu aktivieren.")
