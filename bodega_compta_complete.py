
# streamlit_app.py
import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO

# ---------------------------
# CONFIG & THEME
# ---------------------------
st.set_page_config(page_title="BODEGA - Comptabilité", page_icon="🍷", layout="wide")

# --- Petite touche de style globale ---
CUSTOM_CSS = """
<style>
/* Réduire l’espace vertical global */
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }

/* Rendre les DataFrames plus lisibles */
.dataframe tr:hover td { background-color: #fafafa !important; }
.dataframe th { background: #f7f7f7 !important; }

/* Badge d'état */
.badge {
  display: inline-block; padding: 0.25rem 0.6rem; border-radius: 999px; 
  font-size: 0.85rem; font-weight: 600; line-height: 1; letter-spacing: .2px;
}
.badge-ok { background: #E6F4EA; color: #16794C; border: 1px solid #BEE3C3; }
.badge-ko { background: #FDEAEA; color: #8C2F39; border: 1px solid #F5C2C7; }

/* Légères cartes */
.section {
  border: 1px solid #eee; border-radius: 14px; padding: 1rem 1rem 0.6rem 1rem; 
  background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,.03);
  margin-bottom: 1rem;
}

/* Tables */
.small-note { color: #6b7280; font-size: 0.85rem; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------
# DONNÉES COMPTE
# ---------------------------
PLAN_COMPTABLE = {
    "205": "Logiciels", "206": "Droit au bail", "207": "Fonds commercial", "2131": "Bâtiments",
    "2154": "Matériel industriel (cuisine)", "2182": "Matériel de transport", "2183": "Matériel informatique", "2184": "Mobilier",
    "2805": "Amortissements logiciels", "2806": "Amortissements droit au bail", "2807": "Amortissements fonds commercial",
    "28131": "Amortissements bâtiments", "28154": "Amortissements matériel cuisine", "28182": "Amortissements matériel transport",
    "28183": "Amortissements matériel informatique", "28184": "Amortissements mobilier",
    "31": "Matières premières", "321": "Matières consommables", "37": "Stocks de marchandises",
    "401": "Fournisseurs", "404": "Fournisseurs immobilisations", "408": "Factures non parvenues",
    "411": "Clients", "416": "Clients douteux", "421": "Personnel - Rémunérations dues", "431": "Sécurité sociale",
    "437": "Autres organismes sociaux", "445": "TVA", "447": "Autres impôts et taxes", "467": "Autres créances",
    "512": "Banque", "514": "Chèques postaux", "53": "Caisse",
    "101": "Capital", "106": "Réserves", "110": "Report à nouveau", "151": "Provisions pour risques",
    "153": "Provisions grosses réparations", "158": "Autres provisions", "164": "Emprunts auprès établissements crédit",
    "1675": "Emprunts participatifs", "168": "Autres emprunts et dettes assimilées",
    "601": "Achats stockés - Matières premières", "6061": "Fournitures non stockables (eau, énergie)",
    "607": "Achats de marchandises", "6132": "Locations immobilières", "615": "Entretien et réparations",
    "6161": "Primes d'assurances", "6260": "Frais postaux et télécommunications", "621": "Personnel extérieur",
    "641": "Rémunérations du personnel", "645": "Charges sociales", "647": "Autres cotisations sociales",
    "6611": "Intérêts des emprunts", "666": "Pertes de change", "6582": "Pénalités, amendes",
    "6871": "Dotations amortissements exceptionnels", "68111": "Dotations aux amortissements",
    "701": "Ventes de produits finis (hébergement)", "706": "Prestations de services (restaurant)",
    "707": "Produits annexes", "708": "Produits activités diverses", "709": "Rabais accordés",
    "741": "Subventions d'exploitation", "747": "Quote-part subventions investissement",
    "757": "Produits des cessions d'immobilisations", "764": "Revenus des valeurs mobilières",
    "766": "Gains de change", "768": "Autres produits financiers", "7588": "Autres produits exceptionnels"
}

COMPTES_ACTIF = ["205", "206", "207", "2131", "2154", "2182", "2183", "2184", "31", "321", "37", "411", "416", "467", "512", "514", "53"]
COMPTES_PASSIF = ["101", "106", "110", "151", "153", "158", "164", "1675", "168", "401", "404", "408", "421", "431", "437", "445", "447"]
COMPTES_CHARGES = ["601", "6061", "607", "6132", "615", "6161", "6260", "621", "641", "645", "647", "6611", "666", "6582", "6871", "68111"]
COMPTES_PRODUITS = ["701", "706", "707", "708", "709", "741", "747", "757", "764", "766", "768", "7588"]
COMPTES_AMORTISSEMENTS = ["2805", "2806", "2807", "28131", "28154", "28182", "28183", "28184"]

# ---------------------------
# STATE INIT
# ---------------------------
if "journal" not in st.session_state: st.session_state.journal = []
if "operation_en_cours" not in st.session_state: st.session_state.operation_en_cours = []
if "date_op" not in st.session_state: st.session_state.date_op = date(2024, 1, 1)
if "libelle_op" not in st.session_state: st.session_state.libelle_op = ""
if "num_piece_op" not in st.session_state: st.session_state.num_piece_op = "OP001"
if "nom_eleve" not in st.session_state: st.session_state.nom_eleve = ""

# ---------------------------
# HELPERS
# ---------------------------
def euro(x: float) -> str:
    try:
        return f"{x:,.2f} €".replace(",", " ").replace(".", ",")
    except Exception:
        return ""

def lignes_op_df():
    if len(st.session_state.operation_en_cours) == 0:
        return pd.DataFrame(columns=["Compte", "Libellé ligne", "Débit", "Crédit"])
    return pd.DataFrame(st.session_state.operation_en_cours)

def df_style_money(df: pd.DataFrame, debit_col="Débit", credit_col="Crédit"):
    style = df.style.format({debit_col: euro, credit_col: euro}, na_rep="")
    return style

def add_ligne(compte, libelle, debit, credit):
    st.session_state.operation_en_cours.append({
        "Compte": compte,
        "Libellé ligne": libelle,
        "Débit": float(debit),
        "Crédit": float(credit)
    })

def operation_equilibree(lignes) -> bool:
    td = sum(l["Débit"] for l in lignes)
    tc = sum(l["Crédit"] for l in lignes)
    return abs(td - tc) < 0.01

def piece_suivante(piece: str) -> str:
    try:
        digits = "".join([c for c in piece if c.isdigit()])
        letters = "".join([c for c in piece if c.isalpha()])
        if digits:
            new_num = int(digits) + 1
            return f"{letters}{new_num:06d}" if letters else f"OP{new_num:03d}"
    except:
        pass
    return piece

# ---------------------------
# SIDEBAR
# ---------------------------
with st.sidebar:
    st.header("👤 Identification")
    nom_eleve = st.text_input("Nom et prénom de l'élève", value=st.session_state.nom_eleve, placeholder="Ex: Dupont Marie")
    st.session_state.nom_eleve = nom_eleve

    st.markdown("---")
    st.subheader("⚙️ Actions")
    if st.button("🗑️ Effacer tout", type="secondary", help="Réinitialiser le journal et l'opération en cours"):
        st.session_state.journal = []
        st.session_state.operation_en_cours = []
        st.toast("Journal réinitialisé.", icon="🗑️")

# ---------------------------
# HEADER + KPI
# ---------------------------
st.title("🍷 BODEGA — Comptabilité pédagogique")

# KPIs globaux
df_journal = pd.DataFrame(st.session_state.journal) if len(st.session_state.journal) else pd.DataFrame(
    columns=["Date","Libellé opération","N° Pièce","Compte","Intitulé compte","Libellé ligne","Débit","Crédit"]
)
nb_ecritures = len(df_journal)
nb_operations = df_journal["N° Pièce"].nunique() if nb_ecritures else 0
total_debit = float(df_journal["Débit"].sum()) if nb_ecritures else 0.0
total_credit = float(df_journal["Crédit"].sum()) if nb_ecritures else 0.0
equilibre_global = abs(total_debit - total_credit) < 0.01

k1, k2, k3, k4, k5 = st.columns([1,1,1,1,1.2])
k1.metric("Écritures", nb_ecritures)
k2.metric("Opérations", nb_operations)
k3.metric("Total Débit", euro(total_debit))
k4.metric("Total Crédit", euro(total_credit))
with k5:
    st.markdown(
        f'<span class="badge {"badge-ok" if equilibre_global else "badge-ko"}">'
        f'{"✓ Journal équilibré" if equilibre_global else f"✗ Écart : {euro(abs(total_debit-total_credit))}"}'
        f'</span>',
        unsafe_allow_html=True
    )

st.caption("💡 Astuce : saisissez une opération dans l’onglet *Saisie* puis validez quand Débit = Crédit.")

# ---------------------------
# TABS
# ---------------------------
tab_saisie, tab_journal, tab_balance, tab_gl, tab_cr, tab_bilan, tab_export = st.tabs(
    ["✏️ Saisie", "📖 Journal", "⚖️ Balance", "📚 Grand livre", "💰 Résultat", "📊 Bilan", "📥 Export"]
)

# ---------------------------
# TAB SAISIE
# ---------------------------
with tab_saisie:
    st.subheader("Bloc 1 · Informations de l'opération")
    with st.form("form_infos"):
        c1, c2, c3 = st.columns([1.1, 2.5, 1.2])
        with c1:
            date_operation = st.date_input("Date", value=st.session_state.date_op, format="DD/MM/YYYY")
        with c2:
            libelle_operation = st.text_input("Libellé de l'opération", value=st.session_state.libelle_op,
                                              placeholder="Ex: Achat filet de perche (10kg)")
        with c3:
            num_piece = st.text_input("N° Pièce comptable", value=st.session_state.num_piece_op, placeholder="Ex: OP001")

        submitted_infos = st.form_submit_button("Enregistrer ces infos", use_container_width=True)
        if submitted_infos:
            st.session_state.date_op = date_operation
            st.session_state.libelle_op = libelle_operation
            st.session_state.num_piece_op = num_piece
            st.success("Informations mises à jour.")

    st.divider()
    st.subheader("Bloc 2 · Lignes comptables")
    # Affichage des lignes
    if len(st.session_state.operation_en_cours) > 0:
        st.markdown("**Lignes ajoutées :**")
        op_df = lignes_op_df()
        st.dataframe(df_style_money(op_df), use_container_width=True, hide_index=True)
        tdc = float(op_df["Débit"].sum()); tcc = float(op_df["Crédit"].sum())
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Débit", euro(tdc))
        c2.metric("Total Crédit", euro(tcc))
        with c3:
            ok = abs(tdc - tcc) < 0.01
            st.markdown(
                f'<span class="badge {"badge-ok" if ok else "badge-ko"}">'
                f'{"✓ ÉQUILIBRÉ" if ok else f"✗ Écart : {euro(abs(tdc-tcc))}"}'
                f'</span>',
                unsafe_allow_html=True
            )

        # Suppression par ligne
        for idx, ligne in enumerate(st.session_state.operation_en_cours):
            col1, col2, col3, col4, col5 = st.columns([1.3, 3, 2, 2, 0.6])
            with col1: st.text(ligne["Compte"])
            with col2: st.text(ligne["Libellé ligne"])
            with col3: st.text(euro(ligne["Débit"]) if ligne["Débit"] > 0 else "")
