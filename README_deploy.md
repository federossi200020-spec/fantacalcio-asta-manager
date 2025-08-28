
# Fantacalcio Asta Manager (Streamlit)

App web per gestire l'asta del fantacalcio: caricamento CSV, ricerca/filtri, inserimento prezzo reale, ricalcolo stime per i giocatori mancanti, download del CSV aggiornato.

## ✅ Requisiti file
- `fantacalcio_app.py` (questo file avvia l'app)
- `requirements.txt` (dipendenze Python)
- `giocatori_fantacalcio.csv` (CSV di esempio, opzionale: puoi caricarne uno tuo dall'interfaccia)

## ▶️ Esecuzione locale (opzionale)
```bash
pip install -r requirements.txt
streamlit run fantacalcio_app.py
```

## ☁️ Deploy su Streamlit Community Cloud (gratis)
1. Crea un account su GitHub (se non ce l'hai).
2. Crea un repository (es. `fantacalcio-asta-manager`).
3. Carica **tre file**: `fantacalcio_app.py`, `requirements.txt`, `giocatori_fantacalcio.csv`.
4. Vai su https://share.streamlit.io (accedi con GitHub) → **New app**.
5. Seleziona il repo, il branch (es. `main`) e il file principale: `fantacalcio_app.py`.
6. Clicca **Deploy**. Dopo 1-2 minuti avrai un link pubblico.
7. All'avvio puoi:
   - usare il CSV d'esempio già nel repo, oppure
   - caricare dal tuo PC un CSV con le **colonne esatte**: `nome, ruolo, prezzo_stimato, grado, prezzo_asta`.

> Nota: la scrittura su disco su Streamlit Cloud non è persistente. Usa **Scarica CSV** per salvare i progressi e ricaricarli la volta successiva.

## 💡 CSV: formato richiesto
- `nome`: stringa
- `ruolo`: Portiere | Difensore | Centrocampista | Attaccante
- `prezzo_stimato`: numero (anche decimali)
- `grado`: 1-4 (intero)
- `prezzo_asta`: vuoto finché non acquistato, poi numero

## 🔁 Algoritmo di ricalcolo
Per ogni combinazione **ruolo + grado**:
- calcola la media dei `prezzo_asta` dei giocatori **già usciti**,
- applica questa media come `prezzo_stimato` ai giocatori **mancanti** con lo stesso **ruolo** e **grado**.

## 📱 Suggerimenti d'uso
- Usa i **filtri** (ruolo, grado, stato) e la **ricerca** per trovare rapidamente i giocatori.
- Inserisci il **prezzo reale** dalla sezione dedicata.
- Premi **Ricalcola stime** per aggiornare i valori dei mancanti.
- **Scarica il CSV** a fine sessione e ricaricalo nella prossima.

Buona asta! ⚽
