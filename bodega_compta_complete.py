# ==========================================================
# BODEGA – Comptabilité pédagogique (version stabilisée)
# Public : élèves de lycée professionnel
# Logique : Journal → Grand livre → Balance → CR → Bilan
# ==========================================================

import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="BODEGA – Comptabilité pédagogique", layout="centered")

st.title("BODEGA – Comptabilité pédagogique")
st.caption("Application de comptabilité simplifiée – logique bac pro")

# ==========================================================
# PLAN COMPTABLE SIMPLIFIÉ
# ==========================================================
PLAN_COMPTABLE = {
    "101": "Capital",
    "164": "Emprunts",
    "205": "Logiciels",
    "215": "Matériel",
    "218": "Mobilier",
    "31": "Stocks",
    "37": "Marchandises",
    "401": "Fournisseurs",
    "411": "Clients",
    "512": "Banque",
    "53": "Caisse",
    "601": "Achats",
    "606": "Charges externes",
    "641": "Salaires",
    "645": "Charges sociales",
    "661": "Charges financières",
    "671": "Charges exceptionnelles",
    "701": "Ventes",
    "707": "Ventes de marchandises",
    "761": "Produits financiers",
    "771": "Produits exceptionnels"
}

# ==========================================================
# SESSION STATE
# ==========================================================
if "journal" not in st.session_state:
    st.session_state.journal = []

# ==========================================================
# IDENTIFICATION
# ==========================================================
st.subheader("Identification")
st.text_input("Nom et prénom de l'élève")

st.divider()

# ==========================================================
# SAISIE D’UNE ÉCRITURE COMPTABLE
# ==========================================================
st.subheader("📝 Saisie dans le journal")

with st.form("saisie"):
    col1, col2 = st.columns(2)
    with col1:
        date_op = st.date_input("Date", value=date.today())
        piece = st.text_input("Pièce comptable")
    with col2:
        libelle = st.text_input("Libellé de l'opération")

    st.markdown("### Ligne 1")
    c1, c2, c3 = st.columns(3)
    compte1 = c1.selectbox("Compte", PLAN_COMPTABLE.keys(), key="c1")
    debit1 = c2.number_input("Débit", min_value=0.0, step=0.01, key="d1")
    credit1 = c3.number_input("Crédit", min_value=0.0, step=0.01, key="cr1")

    st.markdown("### Ligne 2")
    c4, c5, c6 = st.columns(3)
    compte2 = c4.selectbox("Compte ", PLAN_COMPTABLE.keys(), key="c2")
    debit2 = c5.number_input("Débit ", min_value=0.0, step=0.01, key="d2")
    credit2 = c6.number_input("Crédit ", min_value=0.0, step=0.01, key="cr2")

    valider = st.form_submit_button("Ajouter au journal")

if valider:
    total_debit = debit1 + debit2
    total_credit = credit1 + credit2

    if total_debit != total_credit:
        st.error("Le total du débit doit être égal au total du crédit.")
    else:
        st.session_state.journal.append({
            "Date": date_op,
            "Pièce": piece,
            "Libellé": libelle,
            "Compte": compte1,
            "Intitulé": PLAN_COMPTABLE[compte1],
            "Débit": debit1,
            "Crédit": credit1
        })
        st.session_state.journal.append({
            "Date": date_op,
            "Pièce": piece,
            "Libellé": libelle,
            "Compte": compte2,
            "Intitulé": PLAN_COMPTABLE[compte2],
            "Débit": debit2,
            "Crédit": credit2
        })
        st.success("Écriture enregistrée.")

st.divider()

# ==========================================================
# JOURNAL COMPTABLE
# ==========================================================
st.subheader("📘 Journal comptable")

if st.session_state.journal:
    df = pd.DataFrame(st.session_state.journal)
    st.dataframe(df, use_container_width=True)

    with st.expander("📖 Expliquer le journal comptable"):
        st.markdown("""
Le journal comptable est le **document de base**.

Tout ce que tu enregistres commence ici.
Chaque opération comporte **au moins deux lignes** :
- une au débit
- une au crédit

👉 Le débit montre ce que l’entreprise **reçoit**  
👉 Le crédit montre ce que l’entreprise **donne**

⚠️ Le total du débit doit toujours être égal au total du crédit.
""")
else:
    st.info("Aucune écriture enregistrée.")

st.divider()

# ==========================================================
# ÉTATS COMPTABLES
# ==========================================================
if st.session_state.journal:
    # ----------------------
    # BALANCE
    # ----------------------
    st.subheader("⚖️ Balance")
    balance = df.groupby(["Compte", "Intitulé"]).agg({"Débit": "sum", "Crédit": "sum"}).reset_index()
    balance["Solde débiteur"] = (balance["Débit"] - balance["Crédit"]).clip(lower=0)
    balance["Solde créditeur"] = (balance["Crédit"] - balance["Débit"]).clip(lower=0)
    st.dataframe(balance, use_container_width=True)

    with st.expander("📖 Expliquer la balance"):
        st.markdown("""
La balance sert à **vérifier** la comptabilité.

Tu y retrouves chaque compte avec :
- le total au débit
- le total au crédit
- le solde

👉 Si le total des débits est différent du total des crédits,
il y a une erreur dans la saisie.
""")

    st.divider()

    # ----------------------
    # GRAND LIVRE
    # ----------------------
    st.subheader("📚 Grand livre")
    compte_sel = st.selectbox("Choisis un compte", balance["Compte"])
    gl = df[df["Compte"] == compte_sel].copy()
    gl["Solde"] = (gl["Débit"] - gl["Crédit"]).cumsum()
    st.dataframe(gl[["Date", "Pièce", "Libellé", "Débit", "Crédit", "Solde"]], use_container_width=True)

    with st.expander("📖 Expliquer le grand livre"):
        st.markdown("""
Le grand livre permet de suivre **un compte à la fois**.

Tu peux voir :
- toutes les opérations du compte
- son évolution
- son solde final

👉 C’est comme un relevé bancaire, mais pour chaque compte.
""")

    st.divider()

    # ----------------------
    # COMPTE DE RÉSULTAT
    # ----------------------
    st.subheader("💰 Compte de résultat")
    charges = balance[balance["Compte"].str.startswith("6")]
    produits = balance[balance["Compte"].str.startswith("7")]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Charges**")
        st.dataframe(charges[["Compte", "Intitulé", "Débit"]])
        total_charges = charges["Débit"].sum()
    with col2:
        st.markdown("**Produits**")
        st.dataframe(produits[["Compte", "Intitulé", "Crédit"]])
        total_produits = produits["Crédit"].sum()

    resultat = total_produits - total_charges
    st.info(f"Résultat : {resultat:.2f} €")

    with st.expander("📖 Expliquer le compte de résultat"):
        st.markdown("""
Le compte de résultat permet de savoir si l’entreprise
a **gagné ou perdu de l’argent**.

Résultat = Produits – Charges

👉 Résultat positif : bénéfice  
👉 Résultat négatif : perte
""")

    st.divider()

    # ----------------------
    # BILAN
    # ----------------------
    st.subheader("🧾 Bilan")
    actif = balance[balance["Compte"].str.startswith(("2", "3", "5"))]
    passif = balance[balance["Compte"].str.startswith(("1", "4"))]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Actif**")
        st.dataframe(actif[["Compte", "Intitulé", "Solde débiteur"]])
    with col2:
        st.markdown("**Passif**")
        st.dataframe(passif[["Compte", "Intitulé", "Solde créditeur"]])

    with st.expander("📖 Expliquer le bilan"):
        st.markdown("""
Le bilan est une **photo de l’entreprise** à une date donnée.

- L’actif montre ce que l’entreprise possède
- Le passif montre comment c’est financé

⚠️ Le total de l’actif doit être égal au total du passif.
""")
