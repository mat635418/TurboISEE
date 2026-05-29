# NEXUS ISEE Engine (v4.0-Beta)
### Piattaforma B2B di Decision Support e Ottimizzazione Fiscale per CAF e Patronati

NEXUS ISEE Engine è un middleware analitico in Python e Streamlit progettato per colmare il vuoto tecnologico tra i portali istituzionali (INPS) e le reali opportunità di ottimizzazione fiscale lecita per il cittadino. 

Il software permette agli operatori di sportello di confrontare la DSU Precompilata INPS con uno scenario ottimizzato "A Miglior Favore", quantificando immediatamente il risparmio economico reale sulle agevolazioni pubbliche (Tasse Universitarie, Assegno Unico, Bonus Nido) e proteggendo il CAF da responsabilità civile grazie a un tracciamento normativo trasparente.

---

## 🚀 Funzionalità Chiave

1. **Motore di Calcolo ISEE Rigoroso**: Riproduce fedelmente le formule ministeriali per ISR (Reddito), ISP (Patrimonio), ISE e ISEE basato sulla Scala di Equivalenza e relative maggiorazioni.
2. **Algoritmi di Ottimizzazione Attivi (Lecita ed Etica)**:
   - **Ottimizzazione Canone di Locazione**: Verifica la corretta inclusione di spese accessorie o contratti integrativi.
   - **Riallocazione Quote Patrimoniali & Mutui**: Bilanciamento delle franchigie sulla prima casa in caso di co-intestazione.
   - **Ottimizzazione Saldo vs Giacenza**: Applicazione automatica dell'Art. 5 DPCM 159/2013 per anomalie da investimenti o acquisti durevoli nell'anno.
3. **Audit Trail & Liability Shield**: Ogni variazione suggerita viene motivata a schermo con il relativo riferimento normativo, offrendo una giustificazione tecnica pronta per l'operatore.
4. **Calcolatore d'Impatto dei Benefici**: Traduce il "Delta ISEE" in risparmio monetario effettivo sui principali bonus assistenziali italiani.

---

## 💻 Installazione e Avvio Rapido

1. **Clona o scarica i file del progetto** (`app.py` e `requirements.txt`) in una cartella locale.
2. **Crea un ambiente virtuale (consigliato)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Su Windows usa: venv\Scripts\activate
