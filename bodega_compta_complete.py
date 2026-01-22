# =============================================================
# BODEGA – Comptabilité pédagogique complète (version stabilisée)
# Public : élèves de lycée professionnel (Bac Pro)
# Objectif : comprendre la chaîne comptable complète
# Journal → Grand livre → Balance → Compte de résultat → Bilan
# =============================================================

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="BODEGA – Comptabilité pédagogique", layout="centered")

st.title("🍷 BODEGA – Comptabilité pédagogique")
st.caption("Tu saisis des opérations comptables et tu observes automatiquement les documents comptables.")

# =============================================================
# PLAN COMPTABLE SIMPLIFIÉ ET LISIBLE
# =============================================================
PLAN_COMPTABLE = {
    # ACTIF
    "205": "Logiciels",
    "215": "Matériel",
    "218": "Mobilier",
    "31": "Stocks",
    "37": "Marchandises",
    "411": "Clients",
    "512": "Banque",
    "53": "Caisse",

    # PASSIF
    "101": "Capital",
    "164": "Emprunts",
    "401": "Fournisseurs",
    "421": "Salaires à payer",
    "445": "TVA",

    # CHARGES
    "601": "Achats",
    "606": "Charges externes",
    "613": "Locations",
    "615": "Entretien et réparations",
    "616": "Assurances",
    "641": "Salaires",
    "645": "Charges sociales",
    "661": "Charges financières",
    "671": "Charges exceptionnelles",

    # PRODUITS
    "701": "Ventes",
    "706": "Prestations de services",
    "707": "Ventes de marchandises",
    "761": "Produits financiers",
    "771": "Produits exceptionnels",
}

COMPTES_AFFICHAGE = [f"{k} – {v}" for k, v in PLAN_COMPTABLE.items()]
MAP_COMPTE = {f"{k} – {v}": k for k, v in PLAN_COMPTABLE.items()}

# =============================================================
# SESSION STATE
# =============================================================
if "journal" not in st.session_state:
    st.session_state.journal = []

if "operation" not in st.session_state:
    st.session_state.operation = []

# =============================================================
# IDENTIFICATION
# =============================================================
st.subheader("👤 Identification")
nom_eleve = st.text_input("Nom et prénom")

st.divider()

# =============================================================
# SAISIE D’UNE OPÉRATION
# =============================================================
st.subheader("✏️ Saisie d’une opération comptable")

col1, col2 = st.columns(2)
with col1:
    date_op = st.date_input("Date", value=datetime.today())
with col2:
    piece = st.text_input("N° de pièce", value="OP001")

libelle_op = st.text_input("Libellé de l’opération", placeholder="Ex : Achat de marchandises")

st.markdown("### Ajouter une ligne (effet miroir débit / crédit)")

compte = st.selectbox("Compte", COMPTES_AFFICHAGE)
libelle_ligne = st.text_input("Libellé de la ligne")

col1, col2 = st.columns(2)
with col1:
    debit = st.number_input("Débit", min_value=0.0, step=10.0)
with col2:
    credit = st.number_input("Crédit", min_value=0.0, step=10.0)

if st.button("➕ Ajouter la ligne"):
    if debit > 0 and credit > 0:
        st.error("Une ligne ne peut pas avoir un débit ET un crédit")
    elif debit == 0 and credit == 0:
        st.error("Tu dois saisir un montant")
    else:
        st.session_state.operation.append({
            "Date": date_op.strftime("%d/%m/%Y"),
            "Pièce": piece,
            "Libellé": libelle_op,
            "Compte": MAP_COMPTE[compte],
            "Intitulé": PLAN_COMPTABLE[MAP_COMPTE[compte]],
            "Débit": debit,
            "Crédit": credit
        })

# Affichage des lignes en cours
if st.session_state.operation:
    df_op = pd.DataFrame(st.session_state.operation)
    st.dataframe(df_op, use_container_width=True)

    total_d = df_op['Débit'].sum()
    total_c = df_op['Crédit'].sum()

    if total_d == total_c:
        st.success("Opération équilibrée")
        if st.button("✅ Valider l’opération"):
            st.session_state.journal.extend(st.session_state.operation)
            st.session_state.operation = []
    else:
        st.warning(f"Écart : {abs(total_d - total_c):.2f} €")

st.divider()

# =============================================================
# JOURNAL COMPTABLE
# =============================================================
st.subheader("📘 Journal comptable")

if st.session_state.journal:
    df = pd.DataFrame(st.session_state.journal)
    st.dataframe(df, use_container_width=True)

    with st.expander("📖 Expliquer le journal"):
        st.markdown("""
        Le journal est le **point de départ** de toute la comptabilité.
        Chaque opération y est enregistrée avec au moins **un débit et un crédit**.
        Le total du débit doit toujours être **égal** au total du crédit.
        """)
else:
    st.info("Aucune écriture enregistrée")

st.divider()

# =============================================================
# BALANCE
# =============================================================
st.subheader("⚖️ Balance")

if st.session_state.journal:
    balance = df.groupby(['Compte','Intitulé']).agg({'Débit':'sum','Crédit':'sum'}).reset_index()
    balance['Solde débiteur'] = (balance['Débit'] - balance['Crédit']).clip(lower=0)
    balance['Solde créditeur'] = (balance['Crédit'] - balance['Débit']).clip(lower=0)
    st.dataframe(balance, use_container_width=True)

    with st.expander("📖 Expliquer la balance"):
        st.markdown("""
        La balance permet de **vérifier la comptabilité**.
        Elle liste tous les comptes avec leurs totaux et leurs soldes.
        Si tout est correct, le total des soldes débiteurs est égal au total des soldes créditeurs.
        """)

st.divider()

# =============================================================
# GRAND LIVRE
# =============================================================
st.subheader("📚 Grand livre")

if st.session_state.journal:
    compte_sel = st.selectbox("Choisis un compte", balance['Compte'].unique())
    gl = df[df['Compte'] == compte_sel].copy()
    gl['Solde'] = (gl['Débit'] - gl['Crédit']).cumsum()
    st.dataframe(gl[['Date','Pièce','Libellé','Débit','Crédit','Solde']], use_container_width=True)

    with st.expander("📖 Expliquer le grand livre"):
        st.markdown("""
        Le grand livre détaille **toutes les opérations d’un compte**.
        Tu peux suivre l’évolution de son solde ligne par ligne.
        """)

st.divider()

# =============================================================
# COMPTE DE RÉSULTAT
# =============================================================
st.subheader("💰 Compte de résultat")

if st.session_state.journal:
    charges = balance[balance['Compte'].str.startswith('6')]
    produits = balance[balance['Compte'].str.startswith('7')]

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

    with st.expander("📖 Expliquer le compte de résultat"):
        st.markdown("""
        Le compte de résultat montre si l’entreprise a gagné ou perdu de l’argent.
        Les charges diminuent le résultat.
        Les produits augmentent le résultat.
        """)

st.divider()

# =============================================================
# BILAN
# =============================================================
st.subheader("🧾 Bilan")

if st.session_state.journal:
    actif = balance[balance['Compte'].str.startswith(('2','3','5'))][['Compte','Intitulé','Solde débiteur']]
    passif = balance[balance['Compte'].str.startswith(('1','4'))][['Compte','Intitulé','Solde créditeur']]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Actif**")
        st.dataframe(actif, use_container_width=True)
        total_actif = actif['Solde débiteur'].sum()
    with col2:
        st.markdown("**Passif**")
        st.dataframe(passif, use_container_width=True)
        total_passif = passif['Solde créditeur'].sum()

    if abs(total_actif - total_passif) < 0.01:
        st.success("Bilan équilibré")
    else:
        st.error("Bilan déséquilibré")

    with st.expander("📖 Expliquer le bilan"):
        st.markdown("""
        Le bilan est une **photo du patrimoine** de l’entreprise.
        À gauche : ce qu’elle possède (actif).
        À droite : ce qu’elle doit (passif).
        Les deux totaux doivent être égaux.
        """)
