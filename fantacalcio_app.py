import streamlit as st
import pandas as pd
import json
import os

def load_fattori():
    if os.path.exists("fattori.json"):
        with open("fattori.json", "r") as f:
            return json.load(f)
    else:
        return {"P": [], "D": [], "C": [], "A": []}

def save_fattori(fattori):
    with open("fattori.json", "w") as f:
        json.dump(fattori, f)

def moltiplicatore_ruolo(fattori, ruolo):
    if not fattori.get(ruolo):
        return 1.0
    m = 1.0
    for f in fattori[ruolo]:
        m *= f
    return m

def highlight_usciti(valore):
    if not pd.isna(valore):
        return "background-color: lightgreen; font-weight: bold;"
    return ""

fattori = load_fattori()

if os.path.exists("giocatori_fantacalcio.csv"):
    df = pd.read_csv("giocatori_fantacalcio.csv")
else:
    st.error("❌ File giocatori_fantacalcio.csv non trovato. Caricalo nella cartella!")
    st.stop()

if "prezzo_iniziale" not in df.columns:
    df["prezzo_iniziale"] = df["prezzo_stimato"]

for idx, row in df.iterrows():
    if pd.isna(row.get("prezzo_asta")):
        m = moltiplicatore_ruolo(fattori, row["ruolo"])
        df.at[idx, "prezzo_stimato"] = row["prezzo_iniziale"] * m

st.set_page_config(page_title="Fantacalcio Asta", layout="wide")
st.title("⚽ Fantacalcio – Gestione Asta")

st.sidebar.header("⚙️ Opzioni")

if st.sidebar.button("🔄 Azzera fattori"):
    fattori = {"P": [], "D": [], "C": [], "A": []}
    save_fattori(fattori)
    df["prezzo_stimato"] = df["prezzo_iniziale"]
    st.success("✅ Fattori azzerati, prezzi tornati ai valori iniziali.")

search = st.text_input("🔍 Cerca giocatore o ruolo")

df_show = df.copy()
if search:
    search_lower = search.lower()
    df_show = df_show[
        df_show["nome"].str.lower().str.contains(search_lower) |
        df_show["ruolo"].str.lower().str.contains(search_lower)
    ]

st.subheader("📋 Lista giocatori")
st.dataframe(
    df_show.style.applymap(highlight_usciti, subset=["prezzo_asta"]),
    use_container_width=True
)

st.subheader("✍️ Inserisci prezzo reale")
giocatore = st.selectbox("Scegli giocatore", df["nome"].tolist())
prezzo_reale = st.number_input("Prezzo reale", min_value=1, step=1)

if st.button("Conferma prezzo"):
    idx = df[df["nome"] == giocatore].index[0]
    ruolo = df.at[idx, "ruolo"]
    stimato_iniziale = df.at[idx, "prezzo_iniziale"]

    df.at[idx, "prezzo_asta"] = prezzo_reale
    df.at[idx, "prezzo_stimato"] = prezzo_reale

    fattore = prezzo_reale / stimato_iniziale if stimato_iniziale > 0 else 1
    fattori[ruolo].append(fattore)
    save_fattori(fattori)

    for j, row in df.iterrows():
        if pd.isna(row["prezzo_asta"]):
            m = moltiplicatore_ruolo(fattori, row["ruolo"])
            df.at[j, "prezzo_stimato"] = row["prezzo_iniziale"] * m

    df.to_csv("giocatori_fantacalcio.csv", index=False)
    st.success(f"✅ Aggiornato {giocatore}: prezzo reale {prezzo_reale} salvato!")

df.to_csv("giocatori_fantacalcio.csv", index=False)
