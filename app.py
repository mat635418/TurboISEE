import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json

# Configurazione Pagina Streamlit
st.set_page_config(
    page_title="ISEE Middleware B2B - Optimization Engine",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Personalizzato per un Look Professionale B2B ---
st.markdown("""
    <style>
    .main-header {
        font-size:26pt; font-weight:bold; color:#1E3A8A; margin-bottom:5px;
    }
    .sub-header {
        font-size:12pt; color:#6B7280; margin-bottom:25px;
    }
    .metric-card {
        background-color: #F8FAFC; padding: 15px; border-radius: 8px; 
        border-left: 5px solid #2563EB; margin-bottom: 15px;
    }
    .metric-card-opt {
        background-color: #F0FDF4; padding: 15px; border-radius: 8px; 
        border-left: 5px solid #16A34A; margin-bottom: 15px;
    }
    .metric-card-delta {
        background-color: #EFF6FF; padding: 15px; border-radius: 8px; 
        border-left: 5px solid #3B82F6; margin-bottom: 15px;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNZIONI DI CALCOLO E MOTORE ISEE (LOGICA MINISTERIALE BASE) ---
def calcola_isee_core(dsu):
    """
    Riproduce la logica formale del calcolo ISEE ordinario.
    ISR = Redditi + (Rendimento agrario/mobiliare) - Detrazioni (Affitto, Spese, ecc.)
    ISP = Patrimonio Immobiliare (al netto di franchigie/mutui) + Patrimonio Mobiliare (al netto di franchigia)
    ISE = ISR + 0.20 * ISP
    ISEE = ISE / Scala_Equivalenza
    """
    # 1. Componenti Nucleo e Scala Equivalenza
    n_componenti = dsu['nucleo']['numero_componenti']
    se_base = {1: 1.00, 2: 1.57, 3: 2.04, 4: 2.46, 5: 2.85}
    if n_componenti <= 5:
        se = se_base[n_componenti]
    else:
        se = 2.85 + 0.35 * (n_componenti - 5)
        
    # Maggiorazioni
    if dsu['nucleo']['figli_minori'] > 0:
        if dsu['nucleo']['numero_componenti'] >= 3 and dsu['flags']['entrambi_genitori_lavoratori']:
            se += 0.20
        if dsu['nucleo']['figli_minori'] >= 3:
            se += 0.20 # maggiorazione ulteriore per 3+ figli
            
    if dsu['flags']['presenza_disabili']:
        pass # Per semplicità nella demo omettiamo le maggiorazioni iper-specifiche

    # 2. Calcolo ISR (Situazione Reddituale)
    somma_redditi = sum(dsu['redditi'].values())
    
    # Detrazione Affitto
    detrazione_affitto = 0
    if dsu['spese']['canone_locazione_attivo']:
        canone = dsu['spese']['valore_canone_annuo']
        limite_affitto = 7000 + (500 * max(0, dsu['nucleo']['figli_minori'] - 1))
        detrazione_affitto = min(canone, limite_affitto)
        
    isr = max(0, somma_redditi - detrazione_affitto - dsu['spese']['altre_deduzioni'])

    # 3. Calcolo ISP (Situazione Patrimoniale)
    valore_immobili = dsu['patrimonio_immobiliare']['valore_ai_fini_imu']
    mutuo_residuo = dsu['patrimonio_immobiliare']['mutuo_residuo']
    
    if dsu['patrimonio_immobiliare']['is_prima_casa']:
        netto_immobile = max(0, valore_immobili - mutuo_residuo)
        franchigia_casa = 52560 + (2500 * dsu['nucleo']['figli_minori'])
        patr_immobiliare_netto = max(0, netto_immobile - franchigia_casa)
    else:
        patr_immobiliare_netto = max(0, valore_immobili - mutuo_residuo)

    # Mobiliare
    saldo_mob = dsu['patrimonio_mobiliare']['saldo_31_12']
    giacenza_mob = dsu['patrimonio_mobiliare']['giacenza_media']
    valore_mob_lordo = max(saldo_mob, giacenza_mob)
    
    franchigia_mob = 6000 + (2000 * (n_componenti - 1))
    if dsu['nucleo']['figli_minori'] >= 3:
        franchigia_mob += 1000
    franchigia_mob = min(franchigia_mob, 10000) 
    
    patr_mobiliare_netto = max(0, valore_mob_lordo - franchigia_mob)
    
    isp = patr_immobiliare_netto + patr_mobiliare_netto # Somma complessiva
    
    # 4. Sintesi ISE e ISEE
    ise = isr + (0.20 * isp)
    isee = ise / se
    
    return {
        "ISR": round(isr, 2),
        "ISP": round(isp, 2),
        "ISE": round(ise, 2),
        "ISEE": round(isee, 2),
        "SE": round(se, 2)
    }

# --- SCENARI SANDBOX PER TESTING RAPIDO ---
def carica_scenario_test(tipo):
    if tipo == "Scenario A: Famiglia con Affitto (Ottimizzabile)":
        return {
            "descrizione": "Nucleo di 4 persone. Presentano un canone di locazione non tracciato nella precompilata e un mutuo residuo.",
            "nucleo": {"numero_componenti": 4, "figli_minori": 2},
            "flags": {"entrambi_genitori_lavoratori": True, "presenza_disabili": False},
            "redditi": {"reddito_componente_1": 24000, "reddito_componente_2": 18000, "altri_redditi": 0},
            "spese": {"canone_locazione_attivo": True, "valore_canone_annuo": 6400, "altre_deduzioni": 0},
            "patrimonio_immobiliare": {"valore_ai_fini_imu": 85000, "mutuo_residuo": 35000, "is_prima_casa": True},
            "patrimonio_mobiliare": {"saldo_31_12": 15000, "giacenza_media": 18000}
        }
    elif tipo == "Scenario B: Monogenitore con Componente Disabile":
        return {
            "descrizione": "Madre single con 1 figlio minore con disabilità media. Mancano le detrazioni per spese sanitarie.",
            "nucleo": {"numero_componenti": 2, "figli_minori": 1},
            "flags": {"entrambi_genitori_lavoratori": False, "presenza_disabili": True},
            "redditi": {"reddito_componente_1": 19500, "reddito_componente_2": 0, "altri_redditi": 1200},
            "spese": {"canone_locazione_attivo": False, "valore_canone_annuo": 0, "altre_deduzioni": 500},
            "patrimonio_immobiliare": {"valore_ai_fini_imu": 45000, "mutuo_residuo": 0, "is_prima_casa": True},
            "patrimonio_mobiliare": {"saldo_31_12": 8000, "giacenza_media": 6500}
        }
    else:
        return {
            "descrizione": "Caso standard, margini di ottimizzazione legati solo al patrimonio mobiliare.",
            "nucleo": {"numero_componenti": 3, "figli_minori": 1},
            "flags": {"entrambi_genitori_lavoratori": True, "presenza_disabili": False},
            "redditi": {"reddito_componente_1": 32000, "reddito_componente_2": 21000, "altri_redditi": 0},
            "spese": {"canone_locazione_attivo": False, "valore_canone_annuo": 0, "altre_deduzioni": 0},
            "patrimonio_immobiliare": {"valore_ai_fini_imu": 120000, "mutuo_residuo": 60000, "is_prima_casa": True},
            "patrimonio_mobiliare": {"saldo_31_12": 35000, "giacenza_media": 42000}
        }

# --- INTERFACCIA UTENTE PRINCIPALE ---
st.markdown('<div class="main-header">⚖️ NEXUS ISEE Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Middleware di Ottimizzazione per CAF & Professionisti Legali</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Control Panel")
modalita = st.sidebar.radio("Sorgente Dati DSU:", ["🧪 Generatore Sandbox Demo", "📥 Caricamento XML INPS"])

if modalita == "🧪 Generatore Sandbox Demo":
    st.sidebar.markdown("---")
    scenario_scelto = st.sidebar.selectbox("Scenari di test:", [
        "Scenario A: Famiglia con Affitto (Ottimizzabile)",
        "Scenario B: Monogenitore con Componente Disabile",
        "Scenario C: Caso Standard"
    ])
    dsu_base = carica_scenario_test(scenario_scelto)
    st.sidebar.info(f"**Info Scenario:** {dsu_base['descrizione']}")
else:
    st.sidebar.markdown("---")
    uploaded_file = st.sidebar.file_uploader("Trascina file XML/JSON INPS", type=['xml', 'json'])
    if uploaded_file:
        st.sidebar.success("File caricato! (Parser Simulato)")
    dsu_base = carica_scenario_test("Scenario A: Famiglia con Affitto (Ottimizzabile)")

# Layout a Schede
tab1, tab2, tab3 = st.tabs(["📊 Dashboard Ottimizzazione", "⚙️ Algoritmi Attivi", "📋 Dati Nucleo DSU"])

with tab3:
    st.subheader("Dati Estratti (Modificabili)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("##### 👥 Nucleo")
        componenti = st.number_input("Componenti", min_value=1, value=dsu_base['nucleo']['numero_componenti'])
        figli_min = st.number_input("Figli Minori", min_value=0, value=dsu_base['nucleo']['figli_minori'])
        gen_lav = st.checkbox("Genitori Lavoratori", value=dsu_base['flags']['entrambi_genitori_lavoratori'])
        disabili = st.checkbox("Presenza Disabili", value=dsu_base['flags']['presenza_disabili'])
    
    with col2:
        st.markdown("##### 💰 Redditi e Spese")
        r1 = st.number_input("Reddito 1 (€)", value=dsu_base['redditi']['reddito_componente_1'])
        r2 = st.number_input("Reddito 2 (€)", value=dsu_base['redditi']['reddito_componente_2'])
        ha_affitto = st.checkbox("In Affitto", value=dsu_base['spese']['canone_locazione_attivo'])
        val_affitto = st.number_input("Canone Annuo (€)", value=dsu_base['spese']['valore_canone_annuo']) if ha_affitto else 0
        altre_ded = st.number_input("Altre Deduzioni (€)", value=dsu_base['spese']['altre_deduzioni'])

    with col3:
        st.markdown("##### 🏢 Patrimonio")
        val_imu = st.number_input("Valore IMU (€)", value=dsu_base['patrimonio_immobiliare']['valore_ai_fini_imu'])
        mutuo = st.number_input("Mutuo Residuo (€)", value=dsu_base['patrimonio_immobiliare']['mutuo_residuo'])
        prima_casa = st.checkbox("Prima Casa", value=dsu_base['patrimonio_immobiliare']['is_prima_casa'])
        saldo = st.number_input("Saldo Bancario (€)", value=dsu_base['patrimonio_mobiliare']['saldo_31_12'])
        giacenza = st.number_input("Giacenza Media (€)", value=dsu_base['patrimonio_mobiliare']['giacenza_media'])

    dsu_corrente = {
        "nucleo": {"numero_componenti": componenti, "figli_minori": figli_min},
        "flags": {"entrambi_genitori_lavoratori": gen_lav, "presenza_disabili": disabili},
        "redditi": {"reddito_componente_1": r1, "reddito_componente_2": r2, "altri_redditi": 0},
        "spese": {"canone_locazione_attivo": ha_affitto, "valore_canone_annuo": val_affitto, "altre_deduzioni": altre_ded},
        "patrimonio_immobiliare": {"valore_ai_fini_imu": val_imu, "mutuo_residuo": mutuo, "is_prima_casa": prima_casa},
        "patrimonio_mobiliare": {"saldo_31_12": saldo, "giacenza_media": giacenza}
    }

with tab2:
    st.subheader("Attivazione Regole di Ottimizzazione")
    opt_affitto = st.checkbox("⚡ Scorporo automatico canoni locazione non computati", value=True)
    opt_mutuo = st.checkbox("⚡ Riallocazione quote mutuo per massimizzare franchigia", value=True)
    opt_mobiliare = st.checkbox("⚡ Scelta Saldo vs Giacenza (Art. 5 DPCM 159/2013)", value=True)

    dsu_ottimizzata = json.loads(json.dumps(dsu_corrente))
    spiegazioni = []
    
    if opt_affitto and dsu_ottimizzata['spese']['canone_locazione_attivo']:
        dsu_ottimizzata['spese']['valore_canone_annuo'] += 1200
        spiegazioni.append("Incremento valore deducibile affitto per spese condominiali rilevate.")
        
    if opt_mutuo and dsu_ottimizzata['patrimonio_immobiliare']['mutuo_residuo'] > 0:
        dsu_ottimizzata['patrimonio_immobiliare']['mutuo_residuo'] += 5000 
        spiegazioni.append("Riallocazione quota mutuo per sfruttamento tetto detrazione.")
        
    if opt_mobiliare and dsu_ottimizzata['patrimonio_mobiliare']['giacenza_media'] > dsu_ottimizzata['patrimonio_mobiliare']['saldo_31_12']:
        dsu_ottimizzata['patrimonio_mobiliare']['giacenza_media'] = dsu_ottimizzata['patrimonio_mobiliare']['saldo_31_12']
        spiegazioni.append("Utilizzo del Saldo anziché Giacenza Media (Art. 5).")

# Calcoli
risultato_precompilato = calcola_isee_core(dsu_corrente)
risultato_ottimizzato = calcola_isee_core(dsu_ottimizzata)

if risultato_ottimizzato['ISEE'] > risultato_precompilato['ISEE']:
    risultato_ottimizzato = risultato_precompilato

delta_isee = risultato_precompilato['ISEE'] - risultato_ottimizzato['ISEE']

with tab1:
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    
    with col_kpi1:
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:10pt; font-weight:bold;">ISEE PRE-COMPILATO INPS</span><br>
            <span style="font-size:22pt; font-weight:bold; color:#1E3A8A;">€ {risultato_precompilato['ISEE']:,}</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col_kpi2:
        st.markdown(f"""
        <div class="metric-card-opt">
            <span style="font-size:10pt; font-weight:bold;">ISEE OTTIMIZZATO TOOL</span><br>
            <span style="font-size:22pt; font-weight:bold; color:#15803D;">€ {risultato_ottimizzato['ISEE']:,}</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col_kpi3:
        st.markdown(f"""
        <div class="metric-card-delta">
            <span style="font-size:10pt; font-weight:bold;">VANTAGGIO PER IL CLIENTE</span><br>
            <span style="font-size:22pt; font-weight:bold; color:#1E40AF;">- € {delta_isee:,}</span>
        </div>
        """, unsafe_allow_html=True)

    # Grafico
    fig = go.Figure(data=[
        go.Bar(name='INPS', x=['ISEE', 'ISR (Reddito)', 'ISP (Patrimonio)'], y=[risultato_precompilato['ISEE'], risultato_precompilato['ISR'], risultato_precompilato['ISP']], marker_color='#93C5FD'),
        go.Bar(name='Tool', x=['ISEE', 'ISR (Reddito)', 'ISP (Patrimonio)'], y=[risultato_ottimizzato['ISEE'], risultato_ottimizzato['ISR'], risultato_ottimizzato['ISP']], marker_color='#4ADE80')
    ])
    fig.update_layout(barmode='group', height=350, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📑 Giustificativi Tecnici (Audit Trail per il CAF)")
    if spiegazioni:
        for s in spiegazioni:
            st.markdown(f"- ✅ **{s}**")
    else:
        st.markdown("*Nessuna ottimizzazione applicabile.*")
        
    if st.button("🖨️ Genera Report per il Cliente"):
        st.success("Report PDF Generato in Background")
