# BODEGA – Application de comptabilité pédagogique (version stabilisée)
# Public : Élèves de Bac Pro
# Objectifs :
# - Comprendre la logique débit / crédit (effet miroir)
# - Saisir, corriger et supprimer des écritures
# - Visualiser automatiquement journal, grand livre, balance, CR et bilan

import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="BODEGA – Comptabilité pédagogique", layout="centered")

st.title("BODEGA – Comptabilité pédagogique")
st.caption("Tu saisis comme sur papier, l'application fait les calculs pour toi")

# =====================
# PLAN COMPTABLE SIMPLIFIÉ
# =====================
PLAN_COMPTABLE = {
    "101": "Capital",
    "164": "Emprunts",
    "205": "Logiciels",
    "213": "Constructions",
    "215": "Matériel",
    "218": "Mobilier",
    "31": "Stocks de matières",
    "37": "Stocks de marchandises",
    "401": "Fournisseurs",
    "411": "Clients",
    "421": "Salaires à payer",
    "445": "TVA",
    "512": "Banque",
    "53": "Caisse",
    "601": "Achats",
    "606": "Charges externes",
    "613": "Locations",
    "615": "Entretien",
    "616": "Assurances",
    "641": "Salaires",
    "645": "Charges sociales",
    "661": "Charges financières",
    "671": "Charges exceptionnelles",
    "701": "Ventes de produits",
    "706": "Prestations de services",
    "707": "Ventes de marchandises",
    "761": "Produits financiers",
    "771": "Produits exceptionnels"
}

# =====================
# SESSION STATE
# =====================
if "journal" not in st.session_state:
    st.session_state.journal = []

if "operation" not in st.session_state:
    st.session_state.operation = []

# =====================
# SAISIE D'UNE OPÉRATION (BLOC FIGÉ)
# =====================
st.subheader("📝 Saisie d'une opération")

col1, col2, col3 = st.columns(3)
with col1:
    date_op = st.date_input("Date", value=date.today())
with col2:
    piece = st.text_input("N° de pièce")
with col3:
    libelle_op = st.text_input("Libellé de l'opération")

st.markdown("**Lignes comptables (effet miroir débit / crédit)**")

c1, c2 = st.columns(2)

with c1:
    st.markdown("### 🔵 Débit")
    compte_d = st.selectbox("Compte débit", PLAN_COMPTABLE.keys(), key="cd")
    montant_d = st.number_input("Montant débit", min_value=0.0, step=1.0, key="md")

with c2:
    st.markdown("### 🔴 Crédit")
    compte_c = st.selectbox("Compte crédit", PLAN_COMPTABLE.keys(), key="cc")
    montant_c = st.number_input("Montant crédit", min_value=0.0, step=1.0, key="mc")

if st.button("➕ Ajouter l'écriture"):
    if montant_d == montant_c and montant_d > 0:
        st.session_state.journal.append({
            "Date": date_op,
            "Pièce": piece,
            "Libellé": libelle_op,
            "Compte": compte_d,
            "Intitulé": PLAN_COMPTABLE[compte_d],
            "Débit": montant_d,
            "Crédit": 0
        })
        st.session_state.journal.append({
            "Date": date_op,
            "Pièce": piece,
            "Libellé": libelle_op,
            "Compte": compte_c,
            "Intitulé": PLAN_COMPTABLE[compte_c],
            "Débit": 0,
            "Crédit": montant_c
        })
        st.success("Écriture ajoutée")
    else:
        st.error("Le débit doit être égal au crédit")

st.divider()

# =====================
# JOURNAL COMPTABLE
# =====================
st.subheader("📒 Journal comptable")

if st.session_state.journal:
    df = pd.DataFrame(st.session_state.journal)
    st.dataframe(df, use_container_width=True)

    index_suppr = st.number_input("Numéro de ligne à supprimer", min_value=0, max_value=len(df)-1, step=1)
    if st.button("🗑️ Supprimer la ligne"):
        st.session_state.journal.pop(index_suppr)
        st.experimental_rerun()

# =====================
# ÉTATS COMPTABLES
# =====================
if st.session_state.journal:
    st.divider()
    st.subheader("📚 Grand livre")
    balance = df.groupby(["Compte", "Intitulé"]).agg({"Débit": "sum", "Crédit": "sum"}).reset_index()
    compte_sel = st.selectbox("Choisis un compte", balance["Compte"])
    gl = df[df["Compte"] == compte_sel].copy()
    gl["Solde"] = (gl["Débit"] - gl["Crédit"]).cumsum()
    st.dataframe(gl, use_container_width=True)

    st.divider()
    st.subheader("⚖️ Balance")
    balance["Solde débiteur"] = (balance["Débit"] - balance["Crédit"]).clip(lower=0)
    balance["Solde créditeur"] = (balance["Crédit"] - balance["Débit"]).clip(lower=0)
    st.dataframe(balance, use_container_width=True)

    st.divider()
    st.subheader("💰 Compte de résultat")
    charges = balance[balance["Compte"].str.startswith("6")]["Débit"].sum()
    produits = balance[balance["Compte"].str.startswith("7")]["Crédit"].sum()
    resultat = produits - charges
    st.write(f"Total charges : {charges:.2f} €")
    st.write(f"Total produits : {produits:.2f} €")
    st.success(f"Résultat : {resultat:.2f} €" if resultat >= 0 else f"Résultat : {resultat:.2f} €")

    st.divider()
    st.subheader("🧾 Bilan")
    actif = balance[balance["Compte"].str.startswith(("2", "3", "5"))]["Solde débiteur"].sum()
    passif = balance[balance["Compte"].str.startswith(("1", "4"))]["Solde créditeur"].sum()
    st.write(f"Total actif : {actif:.2f} €")
    st.write(f"Total passif : {passif:.2f} €")

    st.divider()
    with st.expander("📖 Expliquer ce document (version élève)"):
        st.markdown("""
        - Tu saisis une opération avec **un débit et un crédit du même montant**.
        - Le **journal** enregistre toutes les écritures.
        - Le **grand livre** montre l'évolution d'un compte.
        - La **balance** vérifie que tout est équilibré.
        - Le **compte de résultat** calcule le bénéfice ou la perte.
        - Le **bilan** montre ce que l'entreprise possède et doit.
        """)
