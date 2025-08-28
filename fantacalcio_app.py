
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fantacalcio Asta Manager", layout="wide")

DEFAULT_FILE = "giocatori_fantacalcio.csv"

# ---------- Helpers ----------
def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    expected = ["nome", "ruolo", "prezzo_stimato", "grado", "prezzo_asta"]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Mancano colonne nel CSV: {missing}. Colonne attese: {expected}")
    # tipizzazione
    df["prezzo_stimato"] = pd.to_numeric(df["prezzo_stimato"], errors="coerce")
    df["grado"] = pd.to_numeric(df["grado"], errors="coerce").astype("Int64")
    df["prezzo_asta"] = pd.to_numeric(df["prezzo_asta"], errors="coerce")
    return df

def load_default() -> pd.DataFrame:
    try:
        df = pd.read_csv(DEFAULT_FILE)
        return ensure_columns(df)
    except Exception:
        # CSV non presente: ritorna struttura vuota
        return pd.DataFrame(columns=["nome", "ruolo", "prezzo_stimato", "grado", "prezzo_asta"])

def ricalcola_stime(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    chiamati = df[df["prezzo_asta"].notna()]
    if chiamati.empty:
        return df
    for (ruolo, grado), gruppo in chiamati.groupby(["ruolo", "grado"], dropna=False):
        media = gruppo["prezzo_asta"].mean()
        mask = (df["ruolo"] == ruolo) & (df["grado"] == grado) & (df["prezzo_asta"].isna())
        df.loc[mask, "prezzo_stimato"] = round(float(media), 1)
    return df

def add_player(df: pd.DataFrame, nome: str, ruolo: str, stima: float, grado: int) -> pd.DataFrame:
    nuovo = {"nome": nome, "ruolo": ruolo, "prezzo_stimato": float(stima), "grado": int(grado), "prezzo_asta": pd.NA}
    return pd.concat([df, pd.DataFrame([nuovo])], ignore_index=True)

# ---------- Stato ----------
if "df" not in st.session_state:
    st.session_state.df = load_default()
if "filename" not in st.session_state:
    st.session_state.filename = DEFAULT_FILE

# ---------- Sidebar ----------
st.sidebar.title("⚙️ Impostazioni")
uploaded = st.sidebar.file_uploader("📂 Carica CSV", type=["csv"], help="Formato richiesto: nome, ruolo, prezzo_stimato, grado, prezzo_asta")
if uploaded is not None:
    df_up = pd.read_csv(uploaded)
    st.session_state.df = ensure_columns(df_up)
    st.session_state.filename = uploaded.name

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Ricalcola stime", use_container_width=True):
    st.session_state.df = ricalcola_stime(st.session_state.df)
    st.sidebar.success("Stime aggiornate")

# ---------- Header ----------
st.title("⚽ Fantacalcio Asta Manager")
st.caption("Gestione asta: ricerca, prezzi reali, ricalcolo stime.")

# ---------- Filtri ----------
df = st.session_state.df
if df.empty:
    st.info("Carica un CSV oppure aggiungi manualmente i giocatori dalla sezione in basso.")
else:
    ruoli = sorted([x for x in df["ruolo"].dropna().unique().tolist()])
    gradi = sorted([int(x) for x in df["grado"].dropna().unique().tolist()])

    c1, c2, c3, c4 = st.columns([2, 1.2, 1, 1])
    search = c1.text_input("🔍 Cerca nome o ruolo", placeholder="es. 'Lautaro' o 'Attaccante'")
    role_sel = c2.multiselect("Ruolo", ruoli)
    grado_sel = c3.multiselect("Grado", gradi)
    stato_sel = c4.multiselect("Stato", ["Mancante", "Uscito"])

    df_show = df.copy()
    df_show["Stato"] = df_show["prezzo_asta"].notna().map({True: "Uscito", False: "Mancante"})

    mask = pd.Series([True] * len(df_show))
    if search:
        mask &= df_show["nome"].str.contains(search, case=False, na=False) | df_show["ruolo"].str.contains(search, case=False, na=False)
    if role_sel:
        mask &= df_show["ruolo"].isin(role_sel)
    if grado_sel:
        mask &= df_show["grado"].isin(grado_sel)
    if stato_sel:
        mask &= df_show["Stato"].isin(stato_sel)

    df_filtered = df_show[mask].copy()

    # Tabs di visualizzazione
    tab_all, tab_miss, tab_out = st.tabs(["📋 Tutti (filtrati)", "🟥 Mancanti", "🟢 Usciti"])
    with tab_all:
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)
    with tab_miss:
        st.dataframe(df_filtered[df_filtered["Stato"] == "Mancante"], use_container_width=True, hide_index=True)
    with tab_out:
        st.dataframe(df_filtered[df_filtered["Stato"] == "Uscito"], use_container_width=True, hide_index=True)

# ---------- Aggiornamento prezzo ----------
st.markdown("### ✏️ Inserisci prezzo reale (giocatore chiamato)")
if st.session_state.df.empty:
    st.warning("Nessun giocatore disponibile. Carica un CSV o aggiungi un giocatore.")
else:
    mancanti = st.session_state.df[st.session_state.df["prezzo_asta"].isna()]
    nome_sel = st.selectbox("Giocatore mancante", mancanti["nome"].tolist())
    prezzo = st.number_input("Prezzo d'asta", min_value=1, step=1)
    colu1, colu2 = st.columns([1,1])
    if colu1.button("✅ Salva prezzo"):
        st.session_state.df.loc[st.session_state.df["nome"] == nome_sel, "prezzo_asta"] = prezzo
        st.success(f"Prezzo salvato per {nome_sel}")
    if colu2.button("🔄 Ricalcola subito le stime"):
        st.session_state.df = ricalcola_stime(st.session_state.df)
        st.success("Stime aggiornate")

# ---------- Aggiungi giocatore manualmente ----------
st.markdown("### ➕ Aggiungi nuovo giocatore")
with st.form("add_player"):
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    nome_new = c1.text_input("Nome")
    ruolo_new = c2.selectbox("Ruolo", ["Portiere", "Difensore", "Centrocampista", "Attaccante"])
    stima_new = c3.number_input("Prezzo ipotetico", min_value=0.0, step=0.5, value=0.0)
    grado_new = c4.selectbox("Grado (1=base, 4=top)", [1,2,3,4], index=0)
    submitted = st.form_submit_button("Aggiungi")
    if submitted:
        if not nome_new:
            st.error("Inserisci il nome del giocatore.")
        else:
            st.session_state.df = add_player(st.session_state.df, nome_new, ruolo_new, stima_new, grado_new)
            st.success(f"Giocatore aggiunto: {nome_new}")

# ---------- Download ----------
st.markdown("### ⬇️ Esporta CSV aggiornato")
csv_bytes = st.session_state.df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Scarica CSV",
    data=csv_bytes,
    file_name=st.session_state.filename if st.session_state.filename else "giocatori_fantacalcio.csv",
    mime="text/csv"
)

st.caption("Suggerimento: su Streamlit Cloud, i dati non sono persistenti tra riavvii. Usa il pulsante di download per salvare il CSV aggiornato sul tuo dispositivo.")
