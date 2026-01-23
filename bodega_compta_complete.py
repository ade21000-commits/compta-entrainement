# BODEGA – Application de comptabilité pédagogique (VERSION FINALE STABLE)
# Public : Élèves de Bac Pro
# Principe : saisie miroir débit / crédit sur DEUX LIGNES VISUELLES
# ⚠️ La structure de saisie ne doit PLUS être modifiée

import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="BODEGA – Comptabilité pédagogique", layout="centered")

st.title("BODEGA – Comptabilité pédagogique")
st.caption("Tu saisis comme sur ta feuille, l'application calcule pour toi")

# =====================
# PLAN COMPTABLE (NUMÉRO + INTITULÉ)
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

COMPTES_AFFICHAGE = [f"{k} – {v}" for k, v in PLAN_COMPTABLE.items()]

# =====================
# SESSION STATE
# =====================
if "journal" not in st.session_state:
    st.session_state.journal = []

# =====================
# SAISIE D'UNE OPÉRATION (STRUCTURE VALIDÉE)
# =====================
st.subheader("📝 Saisie d'une opération")

col1, col2, col3 = st.columns(3)
with col1:
    date_op = st.date_input("Date", value=date.today())
with col2:
    piece = st.text_input("N° de pièce")
with col3:
    libelle = st.text_input("Libellé de l'opération")

st.markdown("### Écriture comptable (effet miroir)")

# ----- LIGNE DÉBIT -----
st.markdown("**Débit**")
col_d1, col_d2 = st.columns([3, 1])
with col_d1:
    compte_d_aff = st.selectbox("Compte débité", COMPTES_AFFICHAGE, key="cd")
with col_d2:
    montant_d = st.number_input("Montant", min_value=0.0, step=1.0, key="md")

# ----- LIGNE CRÉDIT -----
st.markdown("**Crédit**")
col_c1, col_c2 = st.columns([3, 1])
with col_c1:
    compte_c_aff = st.selectbox("Compte crédité", COMPTES_AFFICHAGE, key="cc")
with col_c2:
    montant_c = st.number_input("Montant ", min_value=0.0, step=1.0, key="mc")

if st.button("➕ Enregistrer l'écriture"):
    if montant_d == montant_c and montant_d > 0:
        compte_d = compte_d_aff.split(" – ")[0]
        compte_c = compte_c_aff.split(" – ")[0]

        st.session_state.journal.append({
            "Date": date_op,
            "Pièce": piece,
            "Libellé": libelle,
            "Compte": compte_d,
            "Intitulé": PLAN_COMPTABLE[compte_d],
            "Débit": montant_d,
            "Crédit": 0
        })
        st.session_state.journal.append({
            "Date": date_op,
            "Pièce": piece,
            "Libellé": libelle,
            "Compte": compte_c,
            "Intitulé": PLAN_COMPTABLE[compte_c],
            "Débit": 0,
            "Crédit": montant_c
        })
        st.success("Écriture enregistrée")
    else:
        st.error("Le débit doit être égal au crédit")

st.divider()

# =====================
# JOURNAL COMPTABLE (MODIFIABLE)
# =====================
st.subheader("📒 Journal comptable")

if st.session_state.journal:
    df = pd.DataFrame(st.session_state.journal)
    st.dataframe(df, use_container_width=True)

    ligne = st.number_input("Numéro de ligne à supprimer", min_value=0, max_value=len(df)-1, step=1)
    if st.button("🗑️ Supprimer la ligne"):
        st.session_state.journal.pop(ligne)
        st.experimental_rerun()

# =====================
# ÉTATS COMPTABLES ESSENTIELS
# =====================
if st.session_state.journal:
    st.divider()

    st.subheader("📚 Grand livre")
    balance = df.groupby(["Compte", "Intitulé"], as_index=False)[['Débit', 'Crédit']].sum()
    balance["Affichage"] = balance["Compte"] + " – " + balance["Intitulé"]
    compte_sel = st.selectbox("Choisis un compte", balance["Affichage"])
    num_compte = compte_sel.split(" – ")[0]

    gl = df[df["Compte"] == num_compte].copy()
    gl["Solde"] = (gl["Débit"] - gl["Crédit"]).cumsum()
    st.dataframe(gl, use_container_width=True)

    st.divider()
    st.subheader("⚖️ Balance")
    balance["Solde débiteur"] = (balance["Débit"] - balance["Crédit"]).clip(lower=0)
    balance["Solde créditeur"] = (balance["Crédit"] - balance["Débit"]).clip(lower=0)
    st.dataframe(balance[["Compte","Intitulé","Débit","Crédit","Solde débiteur","Solde créditeur"]], use_container_width=True)

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
    actif = balance[balance["Compte"].str.startswith(("2","3","5"))]["Solde débiteur"].sum()
    passif = balance[balance["Compte"].str.startswith(("1","4"))]["Solde créditeur"].sum()

    st.write(f"Total actif : {actif:.2f} €")
    st.write(f"Total passif : {passif:.2f} €")

    with st.expander("📖 Expliquer ce document (version élève)"):
        st.markdown("""
        - Tu saisis une opération avec **un débit et un crédit du même montant**.
        - Chaque compte a un **numéro et un intitulé**, comme au bac.
        - Le journal enregistre tout.
        - Le grand livre suit chaque compte.
        - La balance vérifie l'équilibre.
        - Le compte de résultat calcule le bénéfice ou la perte.
        - Le bilan montre ce que l'entreprise possède et doit.
        """)
