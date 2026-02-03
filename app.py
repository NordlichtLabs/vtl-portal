import hashlib
import time
from datetime import datetime
import pandas as pd
import streamlit as st
from fpdf import FPDF
import base64

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

# --- FUNKTION: PDF GENERIERUNG ---
def create_pdf(cert_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="VTL AUDIT CERTIFICATE", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Reference-ID: {cert_data['p_id']}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {cert_data['date']}", ln=True)
    pdf.cell(200, 10, txt=f"Entropy Sources: {cert_data['entropy_all']}", ln=True)
    pdf.cell(200, 10, txt=f"Protocol-Salt: {cert_data['salt']} (Versiegelt: {cert_data['salt_time']})", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(200, 10, txt="Kryptografischer Master-Hash:", ln=True)
    pdf.set_font("Arial", size=8)
    pdf.multi_cell(0, 5, txt=cert_data['m_hash'])
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"Results: {cert_data['results_str']}", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- 2. DESIGN & STYLING ---
st.set_page_config(page_title="VTL - Verifiable Truth Layer", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #0a0a0a; color: #ffffff; background-image: radial-gradient(circle at 50% 50%, #1a1a1a 0%, #0a0a0a 100%); }
    h1, h2, h3 { font-family: 'Orbitron', sans-serif; letter-spacing: 2px; }
    h1 { color: #00d4ff !important; text-shadow: 0 0 10px #00d4ff; }
    
    .stButton>button { width: 100%; background: linear-gradient(45deg, #004a99, #00d4ff); color: white; font-weight: bold; border-radius: 5px; border: none; height: 45px; transition: 0.3s; }
    
    .use-case-box { padding: 25px; border-radius: 10px; background: rgba(255, 255, 255, 0.03); height: 100%; border-top: 4px solid; }
    .web2-box { border-color: #00d4ff; }
    .web3-box { border-color: #ff00ff; }

    /* Fix für einheitliche Prozess-Karten */
    .hiw-card { 
        background-color: rgba(0, 74, 153, 0.15); 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #004a99;
        height: 180px; /* Feste Höhe für Symmetrie */
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    
    /* Zertifikat kompakter gestaltet */
    .certificate { 
        border: 2px solid #000; 
        padding: 20px 30px; 
        border-radius: 10px; 
        background-color: #ffffff; 
        color: #000000; 
        font-family: 'Courier New', monospace; 
        position: relative; 
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
        max-width: 550px; /* Kompakteres Format */
        margin: auto;
    }
    .cert-label { font-weight: bold; font-size: 11px; color: #555; text-transform: uppercase; margin-top: 8px; }
    .cert-value { font-size: 13px; margin-bottom: 8px; word-break: break-all; color: #000; }
    .cert-title { font-size: 20px; font-weight: bold; text-align: center; border-bottom: 2px solid #000; padding-bottom: 5px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER & INTRO ---
st.title("🛡️ Verifiable Truth Layer (VTL)")
st.write("---")

# --- 4. PROZESS (FIXED SIZE) ---
st.subheader("Der VTL-Prozess")
hiw1, hiw2, hiw3, hiw4 = st.columns(4)
steps = [
    ("1.", "Versiegelung", "Der Protocol-Salt wird im VTL Vault zeitgestempelt versiegelt."),
    ("2.", "Fixierung", "Lotto-Daten werden als Entropy-Hash unveränderbar registriert."),
    ("3.", "Kopplung", "Salt und Entropy verschmelzen kryptografisch zum Master-Hash."),
    ("4.", "Output", "Aus dem Master-Hash entstehen beweisbare Zahlen.")
]
cols = [hiw1, hiw2, hiw3, hiw4]
for i, step in enumerate(steps):
    with cols[i]:
        st.markdown(f'<div class="hiw-card"><div style="color:#00d4ff; font-size:24px; font-weight:bold;">{step[0]}</div><b style="font-size:16px;">{step[1]}</b><div style="font-size:14px; margin-top:10px;">{step[2]}</div></div>', unsafe_allow_html=True)

st.write("---")

# --- 5. VAULT & ENTROPY ---
cv, ce = st.columns(2)
with cv:
    st.header("🔐 Security Vault")
    raw_salt = st.text_input("Protocol-Salt", placeholder="Geben Sie Ihren geheimen Salt ein...")
    if st.button("Salt im Vault registrieren"):
        if raw_salt:
            now = datetime.now().strftime("%H:%M:%S")
            st.session_state.registered_salts.append({"Hash": hashlib.sha256(raw_salt.encode()).hexdigest(), "Salt": raw_salt, "Zeit": now})
            st.rerun()
    if st.session_state.registered_salts:
        ls = st.session_state.registered_salts[-1]
        st.success(f"Status: SEALED | Zeit: {ls['Zeit']}")

with ce:
    st.header("🎰 Entropy Source")
    l_de = st.text_input("Werte DE", "07, 14, 22, 31, 44, 49")
    l_at = st.text_input("Werte AT", "02, 18, 24, 33, 41, 45")
    l_it = st.text_input("Werte IT", "11, 23, 35, 56, 62, 88")

st.write("---")

# --- 6. GENERATOR ---
if st.button("Audit-Zertifikat & Zahlen berechnen"):
    if st.session_state.registered_salts:
        curr = st.session_state.registered_salts[-1]
        today = datetime.now().strftime("%d.%m.%Y")
        e_hash = hashlib.sha256(f"{l_de}{l_at}{l_it}{today}".encode()).hexdigest()
        m_hash = hashlib.sha256(f"{e_hash}-{curr['Salt']}".encode()).hexdigest()
        results = [str(int(m_hash[i:i+2], 16) % 100) for i in range(0, 10, 2)]
        
        st.session_state.current_cert = {
            "p_id": "SEC-AUDIT-Q1", "date": today, "entropy_all": f"{l_de} | {l_at} | {l_it}",
            "salt": curr['Salt'], "salt_time": curr['Zeit'], "m_hash": m_hash, "results_str": ", ".join(results)
        }
    else:
        st.error("Bitte zuerst einen Salt im Vault registrieren!")

if st.session_state.current_cert:
    c = st.session_state.current_cert
    st.markdown(f"""
        <div class='certificate'>
            <div class='cert-title'>VTL AUDIT CERTIFICATE</div>
            <div class='cert-label'>Reference-ID & Date</div>
            <div class='cert-value'>{c['p_id']} | {c['date']}</div>
            <div class='cert-label'>Entropy Sources</div>
            <div class='cert-value'>{c['entropy_all']}</div>
            <div class='cert-label'>Protocol-Salt (Sealed)</div>
            <div class='cert-value'>{c['salt']} (Zeit: {c['salt_time']})</div>
            <div class='cert-label'>Master-Hash</div>
            <div class='cert-value' style='font-size:10px;'>{c['m_hash']}</div>
            <hr style='border: 0.5px solid #ddd; margin: 10px 0;'>
            <p style='text-align:center; font-size:24px; font-weight:bold; color:#000; margin:0;'>{c['results_str']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # PDF Download Button unter dem Zertifikat
    pdf_bytes = create_pdf(c)
    st.download_button(label="📥 Download Audit Certificate (.pdf)", data=pdf_bytes, file_name=f"VTL_Audit_{c['date']}.pdf", mime="application/pdf")
