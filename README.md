# NEXUS ISEE Engine
### Decision Intelligence per CAF e Patronati (stato: v4 Beta, direzione: v5)

NEXUS ISEE Engine è una web app Streamlit che supporta operatori CAF/Patronati nel confronto tra situazione DSU di partenza e scenario ottimizzato, con focus su:
- coerenza del calcolo ISEE;
- riduzione del rischio operativo;
- maggiore trasparenza verso il cittadino.

---

## Visione di prodotto: v5 (sintesi “lessons learned” da v2, v3, v4)

La v5 nasce come convergenza di quattro cicli evolutivi:

- **v2 — Accuratezza di calcolo**  
  Stabilizzazione del motore ISR/ISP/ISE/ISEE e allineamento normativo.

- **v3 — Spiegabilità e fiducia**  
  Introduzione di motivazioni leggibili per ogni suggerimento e tracciabilità delle modifiche.

- **v4 — Operatività di sportello**  
  Interfaccia unica con scenari demo, confronto KPI e vista dati modificabili.

- **v5 — Governance, qualità dati e adozione enterprise**  
  Standardizzazione processo, controlli qualità a monte, monitoraggio KPI di pratica e gestione del rischio percepito da CAF/Patronati.

---

## Cosa potrebbe non piacere ai clienti (e come pre-correggerlo)

### 1) “Non vogliamo black box”
**Rischio:** suggerimenti poco spiegati o percepiti come “automatici”.  
**Pre-correzione:** audit trail esplicito, motivazioni testuali, separazione tra dato originale e dato ottimizzato.

### 2) “Temiamo responsabilità su casistiche borderline”
**Rischio:** bassa fiducia in pratiche complesse o incomplete.  
**Pre-correzione:** policy conservative-by-default, flag delle eccezioni, blocco raccomandazioni su dati incoerenti.

### 3) “Tempi di sportello troppo stretti”
**Rischio:** troppi passaggi manuali.  
**Pre-correzione:** workflow guidato in 3 step (input → validazione → report), modelli scenario e pre-check automatici.

### 4) “Serve prova documentale per ogni scelta”
**Rischio:** contestazioni post-pratica.  
**Pre-correzione:** output con giustificativi tecnici, log delle trasformazioni e riferimenti normativi.

### 5) “L’onboarding del personale è oneroso”
**Rischio:** adozione lenta nelle sedi.  
**Pre-correzione:** UX uniforme, terminologia operativa CAF-first, manuale operativo e checklist pratica.

---

## Stato corrente del repository

- Applicazione principale: `app.py`
- Dipendenze Python: `requirements.txt`

Il codice attuale rappresenta una base funzionale utile per demo e validazione concettuale, con spazio di crescita su robustezza enterprise, controlli qualità dati e automazione operativa.

---

## Installazione

Prerequisiti:
- Python 3.10+
- pip aggiornato

```bash
cd <project_root>
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Avvio applicazione

```bash
cd <project_root>
streamlit run app.py
```

Apri poi l’URL locale mostrato da Streamlit (tipicamente `http://localhost:8501`).

---

## Roadmap v5 consigliata (priorità operativa)

1. **Data Quality Gate**: controlli bloccanti su coerenza dati DSU in input.
2. **Rules Governance**: versionamento regole, changelog normativo e rollback.
3. **Workflow by Role**: profili operatore/revisore/responsabile sede.
4. **Reportistica Enterprise**: report firmabile, storico pratiche, KPI per sede.
5. **Integrazione progressiva**: import strutturato da flussi esterni e riconciliazione automatica.

---

## Note di compliance

Questo progetto ha finalità di supporto decisionale.  
La responsabilità finale sulla pratica resta in capo all’operatore qualificato, che deve verificare la coerenza documentale e normativa prima dell’invio.
