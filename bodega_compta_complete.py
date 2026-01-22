
# bodega_saisie_table.py
import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO

# ---------------------------------
# CONFIG
# ---------------------------------
st.set_page_config(page_title="BODEGA - Saisie tableau", page_icon="🍷", layout="wide")

# ---------------------------------
# PLAN COMPTABLE (codes -> libellés)
# ---------------------------------
PLAN_COMPTABLE = {
    # CLASSE 2 - IMMOBILISATIONS
    "205": "Logiciels", "206": "Droit au bail", "207": "Fonds commercial", "2131": "Bâtiments",
    "2154": "Matériel industriel (cuisine)", "2182": "Matériel de transport", "2183": "Matériel informatique", "2184": "Mobilier",
    # AMORTISSEMENTS
    "2805": "Amortissements logiciels", "2806": "Amortissements droit au bail", "2807": "Amortissements fonds commercial",
    "28131": "Amortissements bâtiments", "28154": "Amortissements matériel cuisine", "28182": "Amortissements matériel transport",
    "28183": "Amortissements matériel informatique", "28184": "Amortissements mobilier",
    # CLASSE 3 - STOCKS
    "31": "Matières premières", "321": "Matières consommables", "37": "Stocks de marchandises",
    # CLASSE 4 - TIERS
    "401": "Fournisseurs", "404": "Fournisseurs immobilisations", "408": "Factures non parvenues",
    "411": "Clients", "416": "Clients douteux", "421": "Personnel - Rémunérations dues", "431": "Sécurité sociale",
    "437": "Autres organismes sociaux", "445": "TVA", "447": "Autres impôts et taxes", "467": "Autres créances",
    # CLASSE 5 - FINANCIER
    "512": "Banque", "514": "Chèques postaux", "53": "Caisse",
    # CLASSE 1 - CAPITAUX
    "101": "Capital", "106": "Réserves", "110": "Report à nouveau",
    "151": "Provisions pour risques", "153": "Provisions grosses réparations", "158": "Autres provisions",
    "164": "Emprunts auprès établissements crédit", "1675": "Emprunts participatifs", "168": "Autres emprunts et dettes assimilées",
    # CLASSE 6 - CHARGES
    "601": "Achats stockés - Matières premières", "6061": "Fournitures non stockables (eau, énergie)",
    "607": "Achats de marchandises", "6132": "Locations immobilières", "615": "Entretien et réparations",
    "6161": "Primes d'assurances", "6260": "Frais postaux et télécommunications", "621": "Personnel extérieur",
    "641": "Rémunérations du personnel", "645": "Charges sociales", "647": "Autres cotisations sociales",
    "6611": "Intérêts des emprunts", "666": "Pertes de change", "6582": "Pénalités, amendes",
    "6871": "Dotations amortissements exceptionnels", "68111": "Dotations aux amortissements",
    # CLASSE 7 - PRODUITS
    "701": "Ventes de produits finis (hébergement)", "706": "Prestations de services (restaurant)",
    "707": "Produits annexes", "708": "Produits activités diverses", "709": "Rabais accordés",
    "741": "Subventions d'exploitation", "747": "Quote-part subventions investissement",
    "757": "Produits des cessions d'immobilisations", "764": "Revenus des valeurs mobilières",
    "766": "Gains de change", "768": "Autres produits financiers", "7588": "Autres produits exceptionnels",
}

# ---------------------------------
# HELPERS
# ---------------------------------
def euro(x: float) -> str:
    try:
        return f"{x:,.2f} €".replace(",", " ").replace(".", ",")
    except Exception:
        return ""

def piece_suivante(piece: str) -> str:
    digits = "".join(c for c in piece if c.isdigit())
    letters = "".join(c for c in piece if c.isalpha())
    try:
        n = int(digits) + 1 if digits else 1
        return f"{letters}{n:06d}" if letters else f"OP{n:03d}"
    except Exception:
        return piece

def account_display(code: str) -> str:
    return f"{code} — {PLAN_COMPTABLE.get(code, '')}" if code else ""

def account_options(codes=None):
    codes = codes or sorted(PLAN_COMPTABLE.keys())
    return [""] + codes

def clean_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Garde les lignes utiles et recalcule l'intitulé depuis le code."""
    df = df.fillna({"Compte":"", "Intitulé compte":"", "Libellé ligne":"", "Débit":0.0, "Crédit":0.0})
    mask = (
        (df["Compte"].astype(str).str.strip() != "") |
        (df["Libellé ligne"].astype(str).str.strip() != "") |
        (df["Débit"].astype(float) > 0) |
        (df["Crédit"].astype(float) > 0)
    )
    df = df[mask].copy()
    df["Intitulé compte"] = df["Compte"].map(PLAN_COMPTABLE).fillna("")
    df["Débit"] = df["Débit"].astype(float)
    df["Crédit"] = df["Crédit"].astype(float)
    return df

# ---------------------------------
# STATE
# ---------------------------------
if "journal" not in st.session_state: st.session_state.journal = []
if "date_op" not in st.session_state: st.session_state.date_op = date.today()
if "libelle_op" not in st.session_state: st.session_state.libelle_op = ""
if "piece" not in st.session_state: st.session_state.piece = "OP001"
if "grid" not in st.session_state:
    st.session_state.grid = pd.DataFrame([{
        "Compte": "", "Intitulé compte": "", "Libellé ligne": "", "Débit": 0.0, "Crédit": 0.0
    }])

# ---------------------------------
# UI
# ---------------------------------
st.title("🍷 BODEGA — Saisie par tableau (avec libellés visibles)")

# En-tête opération
c1, c2, c3 = st.columns([1.15, 2.2, 1.2])
with c1:
    st.session_state.date_op = st.date_input("Date", value=st.session_state.date_op, format="DD/MM/YYYY")
with c2:
    st.session_state.libelle_op = st.text_input("Libellé de l'opération", value=st.session_state.libelle_op, placeholder="Ex: Achat marchandises")
with c3:
    st.session_state.piece = st.text_input("N° Pièce", value=st.session_state.piece, placeholder="Ex: OP001")

st.caption("Choisis un **code** dans la colonne *Compte* → la colonne *Intitulé compte* se remplit automatiquement (ex. 53 — Caisse, 512 — Banque).")

# Tableau de saisie (édition directe)
edited = st.data_editor(
    st.session_state.grid,
    num_rows="dynamic",           # + / – lignes
    use_container_width=True,
    hide_index=True,
    column_config={
        "Compte": st.column_config.SelectboxColumn(
            "Compte",
            options=account_options(),       # tous les comptes
            format_func=account_display,     # ➜ affiche "code — libellé"
            help="Exemples : 53 — Caisse, 512 — Banque"
        ),
        "Intitulé compte": st.column_config.TextColumn(
            "Intitulé compte",
            disabled=True,                   # lecture seule
            width="large"
        ),
        "Libellé ligne": st.column_config.TextColumn(
            "Libellé ligne", max_chars=120, width="medium"
        ),
        "Débit": st.column_config.NumberColumn(
            "Débit", min_value=0.0, step=0.01, format="%.2f"
        ),
        "Crédit": st.column_config.NumberColumn(
            "Crédit", min_value=0.0, step=0.01, format="%.2f"
        ),
    },
    key="editor_grid"
)

# Nettoyage + recalcul des libellés
op_df = clean_rows(edited)

# Conserver l'état (et ajouter une ligne vide si besoin pour fluidifier la saisie)
need_blank = (len(op_df) == 0) or not (op_df.iloc[-1][["Compte","Libellé ligne","Débit","Crédit"]] == ["", "", 0.0, 0.0]).all()
st.session_state.grid = pd.concat(
    [op_df, pd.DataFrame([{"Compte":"", "Intitulé compte":"", "Libellé ligne":"", "Débit":0.0, "Crédit":0.0}])] if need_blank else [op_df],
    ignore_index=True
)

# Totaux + équilibre
total_d = float(op_df["Débit"].sum()) if len(op_df) else 0.0
total_c = float(op_df["Crédit"].sum()) if len(op_df) else 0.0
k1, k2, k3 = st.columns(3)
k1.metric("Total Débit", euro(total_d))
k2.metric("Total Crédit", euro(total_c))
with k3:
    if len(op_df) and abs(total_d - total_c) < 0.01:
        st.success("✓ ÉQUILIBRÉ")
    elif len(op_df):
        st.error(f"✗ Écart : {euro(abs(total_d - total_c))}")

# Vérifs simples par ligne
errors = []
for i, r in op_df.reset_index(drop=True).iterrows():
    code = str(r["Compte"]).strip()
    lib = str(r["Libellé ligne"]).strip()
    d, c = float(r["Débit"]), float(r["Crédit"])
    if code == "":
        errors.append(f"Ligne {i+1} : compte manquant.")
    elif code not in PLAN_COMPTABLE:
        errors.append(f"Ligne {i+1} : code inconnu ({code}).")
    if lib == "":
        errors.append(f"Ligne {i+1} : libellé de ligne manquant.")
    if (d == 0 and c == 0):
        errors.append(f"Ligne {i+1} : saisir un débit **ou** un crédit.")
    if (d > 0 and c > 0):
        errors.append(f"Ligne {i+1} : débit **et** crédit saisis (un seul sens).")

if errors:
    st.warning("À corriger avant validation :")
    for e in errors:
        st.write("•", e)

# Actions
b1, b2 = st.columns([1,1])
with b1:
    disabled = (len(op_df) == 0) or (len(errors) > 0) or (abs(total_d - total_c) >= 0.01) or (not st.session_state.libelle_op.strip())
    if st.button("✅ Valider l'opération", type="primary", use_container_width=True, disabled=disabled):
        for _, row in op_df.iterrows():
            st.session_state.journal.append({
                "Date": st.session_state.date_op.strftime("%d/%m/%Y"),
                "Libellé opération": st.session_state.libelle_op,
                "N° Pièce": st.session_state.piece,
                "Compte": row["Compte"],
                "Intitulé compte": PLAN_COMPTABLE.get(row["Compte"], ""),
                "Libellé ligne": row["Libellé ligne"],
                "Débit": float(row["Débit"]),
                "Crédit": float(row["Crédit"]),
            })
        # reset + incrément pièce
        st.session_state.grid = pd.DataFrame([{
            "Compte": "", "Intitulé compte": "", "Libellé ligne": "", "Débit": 0.0, "Crédit": 0.0
        }])
        st.session_state.piece = piece_suivante(st.session_state.piece)
        st.success("Opération enregistrée dans le journal.")
        st.rerun()

with b2:
    if st.button("❌ Vider le tableau", use_container_width=True, disabled=len(op_df)==0):
        st.session_state.grid = pd.DataFrame([{
            "Compte": "", "Intitulé compte": "", "Libellé ligne": "", "Débit": 0.0, "Crédit": 0.0
        }])
        st.info("Lignes effacées.")
        st.rerun()

st.divider()

# Journal (aperçu + export)
st.subheader("📖 Journal")
if len(st.session_state.journal) == 0:
    st.info("Aucune écriture pour l’instant.")
else:
    J = pd.DataFrame(st.session_state.journal)
    st.dataframe(
        J.style.format({
            "Débit": lambda x: f"{x:,.2f}".replace(",", " ").replace(".", ","),
            "Crédit": lambda x: f"{x:,.2f}".replace(",", " ").replace(".", ","),
        }),
        use_container_width=True, hide_index=True
    )
    td, tc = float(J["Débit"].sum()), float(J["Crédit"].sum())
    cA, cB, cC = st.columns(3)
    cA.metric("Écritures", len(J))
    cB.metric("Total Débit", euro(td))
    cC.metric("Total Crédit", euro(tc))

    st.markdown("#### 📥 Export Excel")
    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        info = pd.DataFrame({
            "Information": ["Date export", "Nb écritures", "Nb opérations"],
            "Valeur": [datetime.now().strftime("%d/%m/%Y %H:%M"), len(J), J["N° Pièce"].nunique()]
        })
        info.to_excel(writer, sheet_name="Informations", index=False)
        J.to_excel(writer, sheet_name="Journal", index=False)
    out.seek(0)
    st.download_button(
        "Télécharger (Excel)",
        data=out,
        file_name=f"Journal_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )
