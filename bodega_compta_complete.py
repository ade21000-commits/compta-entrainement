
# app.py
import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO

st.set_page_config(page_title="BODEGA - Saisie rapide", page_icon="🍷", layout="wide")

# ---------- Plan comptable (mêmes comptes que ton app) ----------
PLAN_COMPTABLE = {
    "205":"Logiciels","206":"Droit au bail","207":"Fonds commercial","2131":"Bâtiments",
    "2154":"Matériel industriel (cuisine)","2182":"Matériel de transport","2183":"Matériel informatique","2184":"Mobilier",
    "2805":"Amortissements logiciels","2806":"Amortissements droit au bail","2807":"Amortissements fonds commercial",
    "28131":"Amortissements bâtiments","28154":"Amortissements matériel cuisine","28182":"Amortissements matériel transport",
    "28183":"Amortissements matériel informatique","28184":"Amortissements mobilier",
    "31":"Matières premières","321":"Matières consommables","37":"Stocks de marchandises",
    "401":"Fournisseurs","404":"Fournisseurs immobilisations","408":"Factures non parvenues",
    "411":"Clients","416":"Clients douteux","421":"Personnel - Rémunérations dues","431":"Sécurité sociale",
    "437":"Autres organismes sociaux","445":"TVA","447":"Autres impôts et taxes","467":"Autres créances",
    "512":"Banque","514":"Chèques postaux","53":"Caisse",
    "101":"Capital","106":"Réserves","110":"Report à nouveau","151":"Provisions pour risques",
    "153":"Provisions grosses réparations","158":"Autres provisions","164":"Emprunts auprès établissements crédit",
    "1675":"Emprunts participatifs","168":"Autres emprunts et dettes assimilées",
    "601":"Achats stockés - Matières premières","6061":"Fournitures non stockables (eau, énergie)",
    "607":"Achats de marchandises","6132":"Locations immobilières","615":"Entretien et réparations",
    "6161":"Primes d'assurances","6260":"Frais postaux et télécommunications","621":"Personnel extérieur",
    "641":"Rémunérations du personnel","645":"Charges sociales","647":"Autres cotisations sociales",
    "6611":"Intérêts des emprunts","666":"Pertes de change","6582":"Pénalités, amendes",
    "6871":"Dotations amortissements exceptionnels","68111":"Dotations aux amortissements",
    "701":"Ventes de produits finis (hébergement)","706":"Prestations de services (restaurant)",
    "707":"Produits annexes","708":"Produits activités diverses","709":"Rabais accordés",
    "741":"Subventions d'exploitation","747":"Quote-part subventions investissement",
    "757":"Produits des cessions d'immobilisations","764":"Revenus des valeurs mobilières",
    "766":"Gains de change","768":"Autres produits financiers","7588":"Autres produits exceptionnels"
}
COMPTES = list(PLAN_COMPTABLE.keys())

# ---------- State ----------
if "journal" not in st.session_state: st.session_state.journal = []  # liste de dict
if "piece" not in st.session_state: st.session_state.piece = "OP001"
if "date_op" not in st.session_state: st.session_state.date_op = date.today()
if "libelle_op" not in st.session_state: st.session_state.libelle_op = ""
if "eleve" not in st.session_state: st.session_state.eleve = ""
if "op_table" not in st.session_state:
    st.session_state.op_table = pd.DataFrame([{"Compte":"", "Libellé ligne":"", "Débit":0.0, "Crédit":0.0}])

# ---------- Helpers ----------
def euro(x: float) -> str:
    try: return f"{x:,.2f} €".replace(",", " ").replace(".", ",")
    except: return ""

def piece_suivante(p: str) -> str:
    digits = "".join(c for c in p if c.isdigit())
    letters = "".join(c for c in p if c.isalpha())
    try:
        n = int(digits) + 1 if digits else 1
        return f"{letters}{n:06d}" if letters else f"OP{n:03d}"
    except:
        return p

# ---------- UI ----------
st.title("🍷 Saisie rapide — Journal")
with st.sidebar:
    st.header("👤 Élève")
    st.session_state.eleve = st.text_input("Nom et prénom", value=st.session_state.eleve, placeholder="Ex: Dupont Marie")
    st.markdown("---")
    if st.button("🗑️ Effacer le journal", type="secondary"):
        st.session_state.journal = []
        st.toast("Journal effacé.", icon="🗑️")

# En-tête opération
c1, c2, c3 = st.columns([1.1, 2.2, 1.2])
with c1:
    st.session_state.date_op = st.date_input("Date", value=st.session_state.date_op, format="DD/MM/YYYY")
with c2:
    st.session_state.libelle_op = st.text_input("Libellé de l'opération", value=st.session_state.libelle_op, placeholder="Ex: Achat marchandises")
with c3:
    st.session_state.piece = st.text_input("N° Pièce", value=st.session_state.piece, placeholder="Ex: OP001")

st.caption("➡️ Complétez le tableau ci-dessous. Une ligne doit avoir **soit** un débit **soit** un crédit (pas les deux).")

# Tableau éditable (on laisse l’utilisateur ajouter/supprimer des lignes)
edited = st.data_editor(
    st.session_state.op_table,
    num_rows="dynamic",                 # permet + / - lignes
    use_container_width=True,
    hide_index=True,
    column_config={
        "Compte": st.column_config.SelectboxColumn(
            "Compte",
            options=[""] + COMPTES,
            required=False,
            help="Choisissez un code (ex: 607, 512...)"
        ),
        "Libellé ligne": st.column_config.TextColumn(
            "Libellé ligne", required=False, max_chars=120, width="medium"
        ),
        "Débit": st.column_config.NumberColumn(
            "Débit", min_value=0.0, step=0.01, format="%.2f", help="Montant au débit (ou 0)"
        ),
        "Crédit": st.column_config.NumberColumn(
            "Crédit", min_value=0.0, step=0.01, format="%.2f", help="Montant au crédit (ou 0)"
        ),
    },
    key="editor"
)

# Nettoyage : ne garder que les lignes "utiles"
def lignes_valides(df: pd.DataFrame) -> pd.DataFrame:
    df = df.fillna({"Compte":"", "Libellé ligne":"", "Débit":0.0, "Crédit":0.0})
    mask_utiles = (df["Compte"].astype(str).str.strip() != "") | \
                  (df["Libellé ligne"].astype(str).str.strip() != "") | \
                  (df["Débit"].astype(float) > 0) | (df["Crédit"].astype(float) > 0)
    return df[mask_utiles].copy()

op_df = lignes_valides(edited)

# Totaux + équilibre
total_d = float(op_df["Débit"].sum()) if len(op_df) else 0.0
total_c = float(op_df["Crédit"].sum()) if len(op_df) else 0.0
col_a, col_b, col_c = st.columns(3)
col_a.metric("Total Débit", euro(total_d))
col_b.metric("Total Crédit", euro(total_c))
with col_c:
    if len(op_df) and abs(total_d - total_c) < 0.01:
        st.success("✓ ÉQUILIBRÉ")
    elif len(op_df):
        st.error(f"✗ Écart : {euro(abs(total_d - total_c))}")

# Vérifications par ligne
errors = []
for i, row in op_df.reset_index(drop=True).iterrows():
    cpt = str(row["Compte"]).strip()
    lib = str(row["Libellé ligne"]).strip()
    d, c = float(row["Débit"] or 0), float(row["Crédit"] or 0)

    if cpt == "": errors.append(f"Ligne {i+1} : compte manquant.")
    elif cpt not in PLAN_COMPTABLE: errors.append(f"Ligne {i+1} : compte inconnu ({cpt}).")
    if lib == "": errors.append(f"Ligne {i+1} : libellé manquant.")
    if (d == 0 and c == 0): errors.append(f"Ligne {i+1} : saisir un débit **ou** un crédit.")
    if (d > 0 and c > 0): errors.append(f"Ligne {i+1} : débit **et** crédit saisis (choisir un seul sens).")

# Boutons action
c_val, c_ann = st.columns([1,1])
with c_val:
    disabled_valider = (len(op_df) == 0) or (len(errors) > 0) or (abs(total_d - total_c) >= 0.01) or (not st.session_state.libelle_op.strip())
    if st.button("✅ Valider l'opération", type="primary", use_container_width=True, disabled=disabled_valider):
        # Ajout au journal
        for _, row in op_df.iterrows():
            st.session_state.journal.append({
                "Date": st.session_state.date_op.strftime("%d/%m/%Y"),
                "Libellé opération": st.session_state.libelle_op,
                "N° Pièce": st.session_state.piece,
                "Compte": row["Compte"],
                "Intitulé compte": PLAN_COMPTABLE.get(row["Compte"], ""),
                "Libellé ligne": row["Libellé ligne"],
                "Débit": float(row["Débit"] or 0),
                "Crédit": float(row["Crédit"] or 0),
            })
        # Reset du tableau + incrément pièce
        st.session_state.op_table = pd.DataFrame([{"Compte":"", "Libellé ligne":"", "Débit":0.0, "Crédit":0.0}])
        st.session_state.piece = piece_suivante(st.session_state.piece)
        st.success("Opération enregistrée dans le journal.")
        st.rerun()
with c_ann:
    if st.button("❌ Vider le tableau", use_container_width=True, disabled=len(op_df)==0):
        st.session_state.op_table = pd.DataFrame([{"Compte":"", "Libellé ligne":"", "Débit":0.0, "Crédit":0.0}])
        st.info("Lignes effacées.")
        st.rerun()

# Affichage des erreurs (si besoin)
if errors:
    st.warning("Merci de corriger avant validation :")
    for e in errors:
        st.write("• ", e)

st.divider()

# -------- Journal minimal --------
st.subheader("📖 Journal")
if len(st.session_state.journal) == 0:
    st.info("Aucune écriture enregistrée pour l’instant.")
else:
    J = pd.DataFrame(st.session_state.journal)
    st.dataframe(
        J.style.format({"Débit": lambda x: f"{x:,.2f}".replace(",", " ").replace(".", ","),
                        "Crédit": lambda x: f"{x:,.2f}".replace(",", " ").replace(".", ",")}),
        use_container_width=True, hide_index=True
    )
    # KPI rapides
    tD, tC = float(J["Débit"].sum()), float(J["Crédit"].sum())
    a,b,c = st.columns(3)
    a.metric("Écritures", len(J))
    b.metric("Total Débit", euro(tD))
    c.metric("Total Crédit", euro(tC))

    # Export (optionnel)
    st.markdown("#### 📥 Export")
    if not st.session_state.eleve.strip():
        st.caption("Renseigne ton nom dans la barre latérale pour nommer le fichier.")
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        info = pd.DataFrame({
            "Information":["Nom élève","Date export","Nb écritures","Nb opérations"],
            "Valeur":[st.session_state.eleve or "Élève", datetime.now().strftime("%d/%m/%Y %H:%M"), len(J), J["N° Pièce"].nunique()]
        })
        info.to_excel(writer, sheet_name="Informations", index=False)
        J.to_excel(writer, sheet_name="Journal", index=False)
    output.seek(0)
    nom_fic = f"{(st.session_state.eleve or 'Eleve').replace(' ','_')}_Bodega_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    st.download_button("Télécharger (Excel)", data=output, file_name=nom_fic,
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")
``
