import streamlit as st
import hashlib
import pandas as pd
from datetime import datetime
import time

# --- KONFIGURATION & DESIGN ---
st.set_page_config(page_title="VTL - Verifiable Truth Layer", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #2e2e2e; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #2e2e2e; border-right: 1px solid #444; }
    .nav-header { font-size: 28px; font-weight: bold; color: #ffffff; margin-bottom: 20px; }
    
    .stButton>button { width: 100%; background-color: #004a99; color: white; font-weight: bold; border-radius: 8px; border: none; height: 45px; }
    .stDownloadButton>button { background-color: #28a745 !important; color: white !important; margin-top: 10px; }
    
    .certificate { 
        border: 2px solid #000; padding: 20px; border-radius: 10px; 
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
    .country-tag { font-weight: bold; color: #90caf9; min-width: 80px; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISIERUNG ---
if 'registered_salts' not in st.session_state:
    st.session_state.registered_salts = []

if 'history_data' not in st.session_state:
    st.session_state.history_data = [
        {"Datum": "03.02.2026", "DE": "12, 45, 67, 23, 89, 10", "AT": "01, 15, 22, 33, 40, 42", "IT": "11, 22, 33, 44, 55, 66", "Hash": "f3b2c1a9e8d7c6b5a49382716059483726150493827160594837261504938271"},
        {"Datum": "02.02.2026", "DE": "05, 14, 28, 33, 41, 44", "AT": "07, 19, 21, 30, 39, 45", "IT": "03, 12, 34, 56, 78, 90", "Hash": "d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5"}
    ]

# --- HEADER LOGIN ---
log_col1, log_col2, log_col3 = st.columns([6, 2, 2])
with log_col2: st.text_input("User", placeholder="E-Mail", label_visibility="collapsed", key="u_login")
with log_col3: st.text_input("Pass", type="password", placeholder="Passwort", label_visibility="collapsed", key="p_login")

st.title("🛡️ Verifiable Truth Layer (VTL)")
st.subheader("Provable Fairness through Multi-Source Entropy & Hashing.")
st.write("---")

# --- SIDEBAR ---
st.sidebar.markdown('<p class="nav-header">🛡️ Navigation</p>', unsafe_allow_html=True)
choice = st.sidebar.radio("Bereich wählen:", ["VTL Generator", "Public Validator"], label_visibility="collapsed")
if st.sidebar.button("🔄 System Reset"):
    st.session_state.registered_salts = []
    st.rerun()

# --- VTL GENERATOR ---
if choice == "VTL Generator":
    col_input1, col_input2 = st.columns([1, 1])
    
    with col_input1:
        st.header("🏢 Firmen-Portal")
        c_name = st.text_input("Firmenname", "BlueBank AG")
        p_id = st.text_input("Projekt-ID", "Audit-Q1-2026")
        raw_salt = st.text_input("Client-Salt", placeholder="Ihr privater Salt...")
        st.markdown('<div style="background-color:#d32f2f; padding:15px; border-radius:5px; text-align:center; color:white; font-weight:bold;">Registration Deadline: 02h 53m 10s</div>', unsafe_allow_html=True)
        if st.button("Client-Salt registrieren"):
            if raw_salt.strip():
                st.session_state.registered_salts.append({"Title": p_id, "Salt": raw_salt, "Zeit": datetime.now().strftime("%H:%M:%S")})
                st.success("✅ Salt sicher im Vault gespeichert.")
        if st.session_state.registered_salts:
            st.dataframe(pd.DataFrame(st.session_state.registered_salts), hide_index=True)

    with col_input2:
        st.header("🎰 Entropy Source")
        today_str = datetime.now().strftime("%d.%m.%Y")
        
        def entropy_row_with_date(label, val, key):
            c_label, c_date = st.columns([1, 1])
            with c_label: st.markdown(f"**{label}**")
            with c_date: st.markdown(f"<p style='text-align:right; color:#ffffff; font-weight:bold; margin:0;'>{today_str}</p>", unsafe_allow_html=True)
            return st.text_input(label, value=val, label_visibility="collapsed", key=key)

        l_de = entropy_row_with_date("Zahlen (DE)", "07, 14, 22, 31, 44, 49", "de")
        l_at = entropy_row_with_date("Zahlen (AT)", "02, 18, 24, 33, 41, 45", "at")
        l_it = entropy_row_with_date("Zahlen (IT)", "11, 23, 35, 56, 62, 88", "it")
        
        m_entropy_combined = f"{l_de}-{l_at}-{l_it}-{today_str}"
        p_hash = hashlib.sha256(m_entropy_combined.encode()).hexdigest()
        
        st.write("---")
        st.header("🧮 Zufall generieren")
        count = st.number_input("Anzahl der Zahlen", min_value=1, value=5)
        r_c1, r_c2, r_c3 = st.columns([2, 1, 2])
        with r_c1: min_v = st.number_input("Von", value=1)
        with r_c3: max_v = st.number_input("Bis", value=1000)
        
        if st.button("Zahlen berechnen & Zertifikat erstellen"):
            if st.session_state.registered_salts:
                current_salt = st.session_state.registered_salts[-1]["Salt"]
                results = []
                for i in range(1, count + 1):
                    h = hashlib.sha256(f"{m_entropy_combined}-{current_salt}-{i}".encode()).hexdigest()
                    num = (int(h, 16) % (max_v - min_v + 1)) + min_v
                    results.append(num)
                
                res_str = ", ".join(map(str, results))
                st.write("---")
                st.header("Zufallszahlen generiert")
                
                res_left, res_right = st.columns([1, 1])
                with res_left:
                    st.table(pd.DataFrame({"Index": range(1, count+1), "Zufallszahl": results}).set_index("Index"))
                    st.markdown(f'<div class="master-hash-display"><b>SHA-256 MASTER HASH (incl. Date):</b><br>{p_hash}</div>', unsafe_allow_html=True)
                
                with res_right:
                    st.markdown(f"""
                    <div class="certificate">
                        <div style="float:right; border:2px solid #000; width:70px; height:70px; text-align:center; font-size:9px; padding-top:15px; font-weight:bold;">QR-CODE</div>
                        <h3 style="margin:0; border-bottom:2px solid #000; font-size:20px;">VTL AUDIT CERTIFICATE</h3>
                        <p style="font-size:12px; margin-top:15px;"><b>PROJEKT:</b> {p_id}<br><b>HALTER:</b> {c_name}<br><b>VALID DATE:</b> {today_str}</p>
                        <p style="font-size:10px; word-break:break-all;"><b>SHA-256 MASTER HASH:</b><br>{p_hash}</p>
                        <hr style="border:1px dashed black;">
                        <p style="margin-bottom:5px;"><b>ERGEBNISSE:</b></p>
                        <p style="font-size:24px; font-weight:bold; color:#004a99 !important; text-align:center; margin:0;">{res_str}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.download_button(label="📥 Download .pdf", data=f"VTL Audit\nDate: {today_str}\nHash: {p_hash}\nResults: {res_str}", file_name=f"VTL_Cert_{today_str}.txt")
            else:
                st.error("❌ Bitte registrieren Sie zuerst einen Client-Salt!")

# --- PUBLIC VALIDATOR (DUMMY VERSION) ---
elif choice == "Public Validator":
    st.title("🔍 Public Validator")
    st.markdown("Verifizieren Sie hier die mathematische Echtheit eines Zertifikats.")
    
    # Textfeld für die ID
    cert_dummy_input = st.text_input("Geben Sie eine Zertifikats ID oder den Master-Hash ein")
    
    # Der Validierungs-Knopf
    if st.button("Validieren"):
        if cert_dummy_input:
            with st.spinner('Kryptografische Kette wird geprüft...'):
                time.sleep(1.2) # Ein bisschen "Rechenzeit" für die Show
                
                # Die gewünschte Dummy-Meldung
                st.success("✅ VALIDIERUNG ERFOLGREICH")
                st.balloons()
                st.info("Ja, dieses Zertifikat wurde genau so mit diesen Lottozahlen erstellt.")
                
                # Optional: Zusätzliches Vertrauen schaffen
                st.markdown("""
                **Prüfprotokoll:**
                - Zeitstempel: **Verifiziert**
                - Multi-Source Entropy (DE+AT+IT): **Übereinstimmend**
                - Hash-Integrität: **Garantiert**
                """)
        else:
            st.warning("Bitte geben Sie eine ID ein, um die Prüfung zu starten.")

# --- HISTORIE ---
st.write("---")
st.header("📜 Globale Entropie-History")
for idx, item in enumerate(st.session_state.history_data):
    h_c1, h_c2, h_c3 = st.columns([2, 5, 2])
    with h_c1: st.write(f"**{item['Datum']}**")
    with h_c2: st.write("Multi-Entropy Source (DE+AT+IT)")
    with h_c3:
        if st.button("Details prüfen", key=f"hist_{idx}"):
            st.session_state.selected_hist_idx = idx if st.session_state.selected_hist_idx != idx else None
            st.rerun()

    if st.session_state.selected_hist_idx == idx:
        st.markdown(f"""
        <div class="detail-box">
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <div><span class="country-tag">🇩🇪 DE:</span> {item['DE']}</div>
                <div><span class="country-tag">🇦🇹 AT:</span> {item['AT']}</div>
                <div><span class="country-tag">🇮🇹 IT:</span> {item['IT']}</div>
            </div>
            <hr style="border:0.5px solid #444; margin: 15px 0;">
            <p style="margin-bottom:5px; font-weight: bold; color: #90caf9;">SHA-256 Verification Hash:</p>
            <p style="font-family: monospace; font-size: 11px; color: #90caf9; word-break: break-all;">{item['Hash']}</p>
        </div>
        """, unsafe_allow_html=True)
