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
# ÉTAPE 1 – OPÉRATION
# =====================
st.subheader("1️⃣ Informations de l'opération")

col1, col2 = st.columns(2)
with col1:
    date_op = st.date_input("Date", value=datetime.today())
with col2:
    num_piece = st.text_input("N° de pièce", value="OP001")

libelle_op = st.text_input("Libellé de l'opération", placeholder="Ex : Achat de marchandises")

st.divider()

# =====================
# ÉTAPE 2 – LIGNES
# =====================
st.subheader("2️⃣ Lignes comptables")

with st.expander("➕ Ajouter une opération (effet miroir débit / crédit)", expanded=True):
    st.markdown("**Ligne 1 : Débit**")
    col1, col2 = st.columns(2)
    with col1:
        compte_debit = st.selectbox(
            "Compte débité",
            options=list(PLAN_COMPTABLE.keys()),
            format_func=lambda x: f"{x} – {PLAN_COMPTABLE[x]}",
            key="compte_debit"
        )
    with col2:
        montant = st.number_input("Montant", min_value=0.0, step=10.0)

    st.markdown("**Ligne 2 : Crédit**")
    compte_credit = st.selectbox(
        "Compte crédité",
        options=list(PLAN_COMPTABLE.keys()),
        format_func=lambda x: f"{x} – {PLAN_COMPTABLE[x]}",
        key="compte_credit"
    )

    if st.button("Ajouter l'opération"):
        if montant == 0:
            st.error("Veuillez saisir un montant")
        elif compte_debit == compte_credit:
            st.error("Les comptes débit et crédit doivent être différents")
        else:
            st.session_state.operation.append({
                "Compte": compte_debit,
                "Intitulé": PLAN_COMPTABLE[compte_debit],
                "Débit": montant,
                "Crédit": 0
            })
            st.session_state.operation.append({
                "Compte": compte_credit,
                "Intitulé": PLAN_COMPTABLE[compte_credit],
                "Débit": 0,
                "Crédit": montant
            })
            st.success("Opération ajoutée (effet miroir respecté)")

# =====================
# AFFICHAGE DES LIGNES
# =====================
if st.session_state.operation:
    st.markdown("### Lignes saisies")
    df_op = pd.DataFrame(st.session_state.operation)
    st.dataframe(df_op, use_container_width=True)

    total_debit = df_op["Débit"].sum()
    total_credit = df_op["Crédit"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total débit", f"{total_debit:.2f} €")
    col2.metric("Total crédit", f"{total_credit:.2f} €")

    if abs(total_debit - total_credit) < 0.01:
        col3.success("Équilibré")
    else:
        col3.error("Non équilibré")

    # =====================
    # VALIDATION
    # =====================
    if st.button("Valider l'opération", disabled=abs(total_debit - total_credit) > 0.01):
        for l in st.session_state.operation:
            st.session_state.journal.append({
                "Date": date_op.strftime("%d/%m/%Y"),
                "Pièce": num_piece,
                "Libellé": libelle_op,
                **l
            })

        st.session_state.operation = []
        st.success("Opération enregistrée")

st.divider()

# =====================
# JOURNAL SIMPLIFIÉ
# =====================
st.subheader("📘 Journal comptable")

if st.session_state.journal:
    df_journal = pd.DataFrame(st.session_state.journal)
    st.dataframe(df_journal, use_container_width=True)
else:
    st.info("Aucune écriture enregistrée")

st.divider()

# =====================
# ÉTATS COMPTABLES
# =====================
st.subheader("📊 États comptables")

col1, col2, col3, col4 = st.columns(4)
with col1:
    show_gl = st.button("📚 Grand livre")
with col2:
    show_balance = st.button("⚖️ Balance")
with col3:
    show_cr = st.button("💰 Compte de résultat")
with col4:
    show_bilan = st.button("🏛️ Bilan")

# =====================
# GRAND LIVRE
# =====================
if st.session_state.journal and show_gl:
    st.markdown("### 📚 Grand livre")
    comptes = sorted(df_journal['Compte'].unique())
    compte_sel = st.selectbox("Compte", comptes)
    gl = df_journal[df_journal['Compte'] == compte_sel].copy()
    gl['Solde'] = (gl['Débit'] - gl['Crédit']).cumsum()
    st.dataframe(gl[['Date', 'Pièce', 'Libellé', 'Débit', 'Crédit', 'Solde']], use_container_width=True)

# =====================
# BALANCE
# =====================
if st.session_state.journal and show_balance:
    st.markdown("### ⚖️ Balance comptable")
    balance = df_journal.groupby('Compte').agg({'Débit': 'sum', 'Crédit': 'sum'}).reset_index()
    balance['Solde débiteur'] = balance.apply(lambda r: r['Débit'] - r['Crédit'] if r['Débit'] > r['Crédit'] else 0, axis=1)
    balance['Solde créditeur'] = balance.apply(lambda r: r['Crédit'] - r['Débit'] if r['Crédit'] > r['Débit'] else 0, axis=1)
    st.dataframe(balance, use_container_width=True)

# =====================
# COMPTE DE RÉSULTAT
# =====================
if st.session_state.journal and show_cr:
    st.markdown("### 💰 Compte de résultat")
    charges = df_journal[df_journal['Compte'].str.startswith('6')].groupby('Compte')[['Débit']].sum().reset_index()
    produits = df_journal[df_journal['Compte'].str.startswith('7')].groupby('Compte')[['Crédit']].sum().reset_index()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Charges**")
        st.dataframe(charges, use_container_width=True)
        total_charges = charges['Débit'].sum()
    with col2:
        st.markdown("**Produits**")
        st.dataframe(produits, use_container_width=True)
        total_produits = produits['Crédit'].sum()

    resultat = total_produits - total_charges
    if resultat >= 0:
        st.success(f"Résultat : Bénéfice de {resultat:.2f} €")
    else:
        st.error(f"Résultat : Perte de {abs(resultat):.2f} €")

# =====================
# BILAN
# =====================
if st.session_state.journal and show_bilan:
    st.markdown("### 🏛️ Bilan")
    balance = df_journal.groupby('Compte').agg({'Débit': 'sum', 'Crédit': 'sum'}).reset_index()
    balance['Solde'] = balance['Débit'] - balance['Crédit']

    actif = balance[(balance['Solde'] > 0) & (balance['Compte'].str.startswith(('2','3','5','41')))]
    passif = balance[(balance['Solde'] < 0) & (balance['Compte'].str.startswith(('1','4')))]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**ACTIF**")
        st.dataframe(actif[['Compte','Solde']], use_container_width=True)
        total_actif = actif['Solde'].sum()
        st.metric("Total Actif", f"{total_actif:.2f} €")
    with col2:
        st.markdown("**PASSIF**")
        passif_display = passif.copy()
        passif_display['Solde'] = passif_display['Solde'].abs()
        st.dataframe(passif_display[['Compte','Solde']], use_container_width=True)
        total_passif = passif_display['Solde'].sum()
        st.metric("Total Passif", f"{total_passif:.2f} €")

    if abs(total_actif - total_passif) < 0.01:
        st.success("Bilan équilibré")
    else:
        st.error("Bilan déséquilibré")
