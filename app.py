import streamlit as st
import hashlib
import pandas as pd
from datetime import datetime

# --- KONFIGURATION & DESIGN ---
st.set_page_config(page_title="VTL - Verifiable Truth Layer", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #2e2e2e; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #2e2e2e; border-right: 1px solid #444; }
    .nav-header { font-size: 28px; font-weight: bold; color: #ffffff; margin-bottom: 20px; }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label { color: #ffffff !important; }

    .stButton>button { width: 100%; background-color: #004a99; color: white; font-weight: bold; border-radius: 8px; border: none; }
    .stDownloadButton>button { background-color: #28a745 !important; color: white !important; width: 100%; }
    
    .stTextInput>div>div>input { background-color: #3d3d3d; color: white; border: 1px solid #555; }
    
    /* Zertifikat Design */
    .certificate { 
        border: 2px solid #000; padding: 25px; border-radius: 10px; 
        background-color: #ffffff; color: #000000;
        font-family: 'Courier New', Courier, monospace;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
    }
    .certificate h3, .certificate p, .certificate b { color: #000000 !important; }

    .master-hash-display {
        background-color: #1a1a1a; padding: 15px; border-radius: 5px;
        border: 1px solid #444; font-family: monospace; margin-top: 10px; color: #90caf9;
        word-break: break-all;
    }

    .detail-box {
        background-color: #1e3a5f; padding: 20px; border-radius: 8px;
        margin-top: 10px; border: 1px solid #004a99;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISIERUNG ---
if 'registered_salts' not in st.session_state:
    st.session_state.registered_salts = []

if 'history_data' not in st.session_state:
    st.session_state.history_data = [
        {"Datum": "2026-02-03", "DE": "12, 45, 67, 23, 89, 10", "AT": "01, 15, 22, 33, 40, 42", "IT": "11, 22, 33, 44, 55, 66", "Hash": "f3b2c1a9e8d7c6b5a49382716059483726150493827160594837261504938271"},
        {"Datum": "2026-02-02", "DE": "05, 14, 28, 33, 41, 44", "AT": "07, 19, 21, 30, 39, 45", "IT": "03, 12, 34, 56, 78, 90", "Hash": "d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5"},
        {"Datum": "2026-02-01", "DE": "21, 22, 09, 15, 30, 48", "AT": "02, 08, 14, 26, 33, 41", "IT": "09, 19, 29, 39, 49, 59", "Hash": "b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8"}
    ]

# --- LOGIN HEADER ---
log_col1, log_col2, log_col3 = st.columns([6, 2, 2])
with log_col2: st.text_input("User", placeholder="E-Mail", label_visibility="collapsed", key="u")
with log_col3: st.text_input("Pass", type="password", placeholder="Passwort", label_visibility="collapsed", key="p")

st.title("🛡️ Verifiable Truth Layer (VTL)")
st.subheader("Verifiable Truth Layer: The Global Standard for Provable Fairness.")
st.write("---")

# --- NAVIGATION ---
st.sidebar.markdown('<p class="nav-header">🛡️ Navigation</p>', unsafe_allow_html=True)
choice = st.sidebar.radio("Bereich wählen:", ["VTL Generator", "Public Validator"], label_visibility="collapsed")
if st.sidebar.button("🔄 System Reset"):
    st.session_state.registered_salts = []
    st.rerun()

# --- VTL GENERATOR SEITE ---
if choice == "VTL Generator":
    col_in1, col_in2 = st.columns([1, 1])
    
    with col_in1:
        st.header("🏢 Firmen-Portal")
        c_name = st.text_input("Firmenname", "BlueBank AG")
        p_id = st.text_input("Projekt-ID", "Quartals-Audit-Q1")
        raw_salt = st.text_input("Client-Salt", placeholder="Geben Sie hier ihren Client-Salt ein")
        st.markdown('<div style="background-color:#d32f2f; padding:15px; border-radius:5px; text-align:center; color:white; font-weight:bold;">Remaining Time to register Client Salt: 02h 53m 10s</div>', unsafe_allow_html=True)
        if st.button("Client-Salt registrieren"):
            if raw_salt.strip():
                st.session_state.registered_salts.append({"Title": p_id, "Salt": raw_salt, "Zeit": datetime.now().strftime("%H:%M:%S")})
                st.success("✅ Registriert")

    with col_in2:
        st.header("🎰 Entropy Source")
        l_de = st.text_input("Zahlen (DE)", "07, 14, 22, 31, 44, 49")
        l_at = st.text_input("Zahlen (AT)", "02, 18, 24, 33, 41, 45")
        l_it = st.text_input("Zahlen (IT)", "11, 23, 35, 56, 62, 88")
        m_entropy = f"{l_de}-{l_at}-{l_it}"
        p_hash = hashlib.sha256(m_entropy.encode()).hexdigest()
        
        st.write("---")
        st.header("🧮 Zufall generieren")
        count = st.number_input("Anzahl", min_value=1, value=5)
        r_c1, r_c2, r_c3 = st.columns([2, 1, 2])
        with r_c1: min_v = st.number_input("Von", value=1)
        with r_c3: max_v = st.number_input("Bis", value=1000)
        
        generate_trigger = st.button("Zahlen berechnen & Zertifikat erstellen")

    # --- DAS NEUE LAYOUT NACH DEM KLICK ---
    if generate_trigger:
        if st.session_state.registered_salts:
            current_salt = st.session_state.registered_salts[-1]["Salt"]
            results = []
            for i in range(1, count + 1):
                h = hashlib.sha256(f"{m_entropy}-{current_salt}-{i}".encode()).hexdigest()
                num = (int(h, 16) % (max_v - min_v + 1)) + min_v
                results.append(num)
            
            st.write("---")
            st.header("Zufallszahlen generiert")
            
            # Hier passiert die Magie: 50/50 Split für Tabelle und Zertifikat
            res_col_left, res_col_right = st.columns([1, 1])
            
            with res_col_left:
                st.table(pd.DataFrame({"Index": range(1, count+1), "Zufallszahl": results}).set_index("Index"))
                st.markdown(f'<div class="master-hash-display"><b>SHA-256 MASTER HASH:</b><br>{p_hash}</div>', unsafe_allow_html=True)
            
            with res_col_right:
                st.markdown(f"""
                <div class="certificate">
                    <div style="float:right; border:2px solid #000; width:70px; height:70px; text-align:center; font-size:9px; padding-top:15px; font-weight:bold;">QR-CODE</div>
                    <h3 style="margin:0; border-bottom:2px solid #000; font-size:20px;">VTL AUDIT CERTIFICATE</h3>
                    <p style="font-size:12px; margin-top:15px;"><b>PROJEKT:</b> {p_id}<br><b>HALTER:</b> {c_name}<br><b>DATE:</b> {datetime.now().strftime("%d.%m.%Y")}</p>
                    <p style="font-size:10px; word-break:break-all;"><b>SHA-256 MASTER HASH:</b><br>{p_hash}</p>
                    <hr style="border:1px dashed black;">
                    <p style="margin-bottom:5px;"><b>ERGEBNISSE:</b></p>
                    <p style="font-size:24px; font-weight:bold; color:#004a99 !important; text-align:center; margin:0;">{", ".join(map(str, results))}</p>
                </div>
                """, unsafe_allow_html=True)
                st.download_button("📥 Download .pdf", data=str(results), file_name=f"VTL_{p_id}.txt")
        else:
            st.error("❌ Bitte erst den Salt registrieren!")

# --- VALIDATOR SEITE ---
elif choice == "Public Validator":
    st.title("🔍 Public Validator")
    st.write("Verifizieren Sie Zertifikate.")

# --- HISTORIE (IMMER UNTEN) ---
st.write("---")
st.header("📜 Globale Entropie-History")
for idx, item in enumerate(st.session_state.history_data):
    c1, c2, c3 = st.columns([2, 5, 2])
    with c1: st.write(f"**{item['Datum']}**")
    with c2: st.write("Multi-Entropy Source (DE+AT+IT)")
    with c3:
        if st.button("Details", key=f"h_{idx}"):
            st.info(f"Länderdaten für {item['Datum']}: DE: {item['DE']} | AT: {item['AT']} | IT: {item['IT']}")
