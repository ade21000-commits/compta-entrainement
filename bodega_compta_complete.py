# Version allégée et plus ergonomique de l'application BODEGA
# Objectifs pédagogiques :
# - Saisie plus rapide
# - Moins de champs visibles en même temps
# - Logique proche des exercices papier (opération puis lignes)

import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="BODEGA - Comptabilité pédagogique", layout="centered")

st.title("BODEGA – Comptabilité pédagogique")
st.caption("Application de saisie comptable simplifiée pour élèves de lycée professionnel")

# =====================
# PLAN COMPTABLE (inchangé)
# =====================
PLAN_COMPTABLE = {
    # =====================
    # ACTIF IMMOBILISÉ (LONG TERME)
    # =====================
    "205": "Logiciels",
    "213": "Constructions",
    "215": "Matériel",
    "218": "Mobilier",

    # =====================
    # ACTIF CIRCULANT (COURT TERME)
    # =====================
    "31": "Stocks de matières",
    "37": "Stocks de marchandises",
    "411": "Clients",
    "512": "Banque",
    "53": "Caisse",

    # =====================
    # PASSIF (MOYEN / LONG TERME)
    # =====================
    "101": "Capital",
    "164": "Emprunts",

    # =====================
    # PASSIF (COURT TERME)
    # =====================
    "401": "Fournisseurs",
    "421": "Salaires à payer",
    "445": "TVA",

    # =====================
    # CHARGES D'EXPLOITATION
    # =====================
    "601": "Achats stockés",
    "606": "Charges externes",
    "613": "Locations",
    "615": "Entretien et réparations",
    "616": "Assurances",
    "641": "Salaires",
    "645": "Charges sociales",

    # =====================
    # PRODUITS D'EXPLOITATION
    # =====================
    "701": "Ventes de produits",
    "706": "Prestations de services",
    "707": "Ventes de marchandises",

    # =====================
    # CHARGES FINANCIÈRES
    # =====================
    "661": "Intérêts des emprunts",
    "666": "Pertes de change",

    # =====================
    # PRODUITS FINANCIERS
    # =====================
    "761": "Produits de participations",
    "766": "Gains de change",

    # =====================
    # CHARGES EXCEPTIONNELLES
    # =====================
    "671": "Charges exceptionnelles",

    # =====================
    # PRODUITS EXCEPTIONNELS
    # =====================
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
# IDENTIFICATION
# =====================
st.subheader("Identification de l'élève")
nom_eleve = st.text_input("Nom et prénom")

st.divider()

# =====================
# ÉTATS COMPTABLES (ESSENTIELS)
# =====================
if st.session_state.journal:
    df_all = pd.DataFrame(st.session_state.journal)

    st.subheader("⚖️ Balance")
    balance = df_all.groupby(['Compte','Intitulé']).agg({'Débit':'sum','Crédit':'sum'}).reset_index()
    balance['Solde débiteur'] = (balance['Débit'] - balance['Crédit']).clip(lower=0)
    balance['Solde créditeur'] = (balance['Crédit'] - balance['Débit']).clip(lower=0)
    st.dataframe(balance, use_container_width=True)

    st.divider()

    st.subheader("📚 Grand livre")
    compte_sel = st.selectbox("Choisir un compte", balance['Compte'].unique())
    gl = df_all[df_all['Compte'] == compte_sel].copy()
    gl['Solde'] = (gl['Débit'] - gl['Crédit']).cumsum()
    st.dataframe(gl[['Date','Pièce','Libellé','Débit','Crédit','Solde']], use_container_width=True)

    st.divider()

    st.subheader("💰 Compte de résultat")
    charges = balance[balance['Compte'].astype(str).str.startswith('6')]
    produits = balance[balance['Compte'].astype(str).str.startswith('7')]
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Charges**")
        st.dataframe(charges[['Compte','Intitulé','Débit']], use_container_width=True)
        total_charges = charges['Débit'].sum()
    with col2:
        st.markdown("**Produits**")
        st.dataframe(produits[['Compte','Intitulé','Crédit']], use_container_width=True)
        total_produits = produits['Crédit'].sum()

    resultat = total_produits - total_charges
    if resultat >= 0:
        st.success(f"Résultat : bénéfice de {resultat:.2f} €")
    else:
        st.error(f"Résultat : perte de {abs(resultat):.2f} €")

    st.divider()

    st.subheader("🧾 Bilan")
    actif = balance[balance['Compte'].astype(str).str.startswith(('2','3','5'))][['Compte','Intitulé','Solde débiteur']]
    passif = balance[balance['Compte'].astype(str).str.startswith(('1','4'))][['Compte','Intitulé','Solde créditeur']]
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Actif**")
        st.dataframe(actif, use_container_width=True)
        st.metric("Total actif", f"{actif['Solde débiteur'].sum():.2f} €")
    with col2:
        st.markdown("**Passif**")
        st.dataframe(passif, use_container_width=True)
        st.metric("Total passif", f"{passif['Solde créditeur'].sum():.2f} €")
