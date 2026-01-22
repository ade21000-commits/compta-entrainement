import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="BODEGA - Comptabilité", layout="wide")

st.title("🍷 BODEGA - Comptabilité Pédagogique Complète")

# PLAN COMPTABLE EXHAUSTIF
PLAN_COMPTABLE = {
    # CLASSE 2 - IMMOBILISATIONS
    "205": "Logiciels",
    "206": "Droit au bail",
    "207": "Fonds commercial",
    "2131": "Bâtiments",
    "2154": "Matériel industriel (cuisine)",
    "2182": "Matériel de transport",
    "2183": "Matériel informatique",
    "2184": "Mobilier",
    
    # AMORTISSEMENTS
    "2805": "Amortissements logiciels",
    "2806": "Amortissements droit au bail",
    "2807": "Amortissements fonds commercial",
    "28131": "Amortissements bâtiments",
    "28154": "Amortissements matériel cuisine",
    "28182": "Amortissements matériel transport",
    "28183": "Amortissements matériel informatique",
    "28184": "Amortissements mobilier",
    
    # CLASSE 3 - STOCKS
    "31": "Matières premières",
    "321": "Matières consommables",
    "37": "Stocks de marchandises",
    
    # CLASSE 4 - TIERS
    "401": "Fournisseurs",
    "404": "Fournisseurs immobilisations",
    "408": "Factures non parvenues",
    "411": "Clients",
    "416": "Clients douteux",
    "421": "Personnel - Rémunérations dues",
    "431": "Sécurité sociale",
    "437": "Autres organismes sociaux",
    "445": "TVA",
    "447": "Autres impôts et taxes",
    "467": "Autres créances",
    
    # CLASSE 5 - FINANCIER
    "512": "Banque",
    "514": "Chèques postaux",
    "53": "Caisse",
    
    # CLASSE 1 - CAPITAUX
    "101": "Capital",
    "106": "Réserves",
    "110": "Report à nouveau",
    "151": "Provisions pour risques",
    "153": "Provisions grosses réparations",
    "158": "Autres provisions",
    "164": "Emprunts auprès établissements crédit",
    "1675": "Emprunts participatifs",
    "168": "Autres emprunts et dettes assimilées",
    
    # CLASSE 6 - CHARGES
    "601": "Achats stockés - Matières premières",
    "6061": "Fournitures non stockables (eau, énergie)",
    "607": "Achats de marchandises",
    "6132": "Locations immobilières",
    "615": "Entretien et réparations",
    "6161": "Primes d'assurances",
    "6260": "Frais postaux et télécommunications",
    "621": "Personnel extérieur",
    "641": "Rémunérations du personnel",
    "645": "Charges sociales",
    "647": "Autres cotisations sociales",
    "6611": "Intérêts des emprunts",
    "666": "Pertes de change",
    "6582": "Pénalités, amendes",
    "6871": "Dotations amortissements exceptionnels",
    "68111": "Dotations aux amortissements",
    
    # CLASSE 7 - PRODUITS
    "701": "Ventes de produits finis (hébergement)",
    "706": "Prestations de services (restaurant)",
    "707": "Produits annexes",
    "708": "Produits activités diverses",
    "709": "Rabais accordés",
    "741": "Subventions d'exploitation",
    "747": "Quote-part subventions investissement",
    "757": "Produits des cessions d'immobilisations",
    "764": "Revenus des valeurs mobilières",
    "766": "Gains de change",
    "768": "Autres produits financiers",
    "7588": "Autres produits exceptionnels"
}

# Catégories pour affichage conditionnel
COMPTES_ACTIF = ["205", "206", "207", "2131", "2154", "2182", "2183", "2184", 
                 "31", "321", "37", "411", "416", "467", "512", "514", "53"]

COMPTES_PASSIF = ["101", "106", "110", "151", "153", "158", "164", "1675", "168",
                  "401", "404", "408", "421", "431", "437", "445", "447"]

COMPTES_CHARGES = ["601", "6061", "607", "6132", "615", "6161", "6260", "621", 
                   "641", "645", "647", "6611", "666", "6582", "6871", "68111"]

COMPTES_PRODUITS = ["701", "706", "707", "708", "709", "741", "747", "757", 
                    "764", "766", "768", "7588"]

COMPTES_AMORTISSEMENTS = ["2805", "2806", "2807", "28131", "28154", "28182", "28183", "28184"]

if 'journal' not in st.session_state:
    st.session_state.journal = []

if 'operation_en_cours' not in st.session_state:
    st.session_state.operation_en_cours = []

if 'date_op' not in st.session_state:
    st.session_state.date_op = "01/01/2024"

if 'libelle_op' not in st.session_state:
    st.session_state.libelle_op = ""

if 'num_piece_op' not in st.session_state:
    st.session_state.num_piece_op = "OP001"

# IDENTIFICATION
st.header("👤 Identification")
nom_eleve = st.text_input("Nom et Prénom de l'élève", placeholder="Ex: Dupont Marie")

# SAISIE OPÉRATION EN 2 BLOCS
st.header("✏️ Saisie d'une opération comptable")

st.subheader("📋 Bloc 1 : Informations de l'opération")

col1, col2, col3 = st.columns(3)
with col1:
    date_operation = st.text_input("Date", value=st.session_state.date_op, key="input_date")
with col2:
    libelle_operation = st.text_input("Libellé de l'opération", 
                                      value=st.session_state.libelle_op,
                                      placeholder="Ex: Achat filet de perche (10kg)",
                                      key="input_libelle")
with col3:
    num_piece = st.text_input("N° Pièce comptable", 
                              value=st.session_state.num_piece_op,
                              placeholder="Ex: 202336",
                              key="input_piece")

# Mise à jour session_state
st.session_state.date_op = date_operation
st.session_state.libelle_op = libelle_operation
st.session_state.num_piece_op = num_piece

st.subheader("📝 Bloc 2 : Lignes comptables de l'opération")

# Afficher les lignes en cours
if len(st.session_state.operation_en_cours) > 0:
    st.markdown("**Lignes ajoutées à cette opération :**")
    
    for idx, ligne in enumerate(st.session_state.operation_en_cours):
        col1, col2, col3, col4, col5 = st.columns([1.5, 4, 2, 2, 0.8])
        
        with col1:
            st.text(ligne['Compte'])
        with col2:
            st.text(ligne['Libellé ligne'])
        with col3:
            st.text(f"{ligne['Débit']:.2f} €" if ligne['Débit'] > 0 else "")
        with col4:
            st.text(f"{ligne['Crédit']:.2f} €" if ligne['Crédit'] > 0 else "")
        with col5:
            if st.button("🗑️", key=f"del_ligne_{idx}"):
                st.session_state.operation_en_cours.pop(idx)
                st.rerun()
    
    # Totaux
    total_debit_op = sum([l['Débit'] for l in st.session_state.operation_en_cours])
    total_credit_op = sum([l['Crédit'] for l in st.session_state.operation_en_cours])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Débit", f"{total_debit_op:.2f} €")
    with col2:
        st.metric("Total Crédit", f"{total_credit_op:.2f} €")
    with col3:
        if abs(total_debit_op - total_credit_op) < 0.01:
            st.success("✓ ÉQUILIBRÉ")
        else:
            st.error(f"✗ Écart : {abs(total_debit_op - total_credit_op):.2f} €")
    
    st.markdown("---")

# Ajout d'une ligne
st.markdown("**Ajouter une ligne :**")

col1, col2, col3, col4 = st.columns([2, 4, 2, 2])

with col1:
    compte_ligne = st.selectbox("Compte", 
                                options=sorted(PLAN_COMPTABLE.keys()),
                                format_func=lambda x: f"{x} - {PLAN_COMPTABLE[x]}",
                                key="select_compte")

with col2:
    libelle_ligne = st.text_input("Libellé de la ligne", 
                                  placeholder="Ex: Achat marchandise filet de perche",
                                  key="input_libelle_ligne")

with col3:
    debit_ligne = st.number_input("Débit", min_value=0.0, value=0.0, step=10.0, key="input_debit")

with col4:
    credit_ligne = st.number_input("Crédit", min_value=0.0, value=0.0, step=10.0, key="input_credit")

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])

with col_btn1:
    if st.button("➕ Ajouter la ligne", type="secondary", use_container_width=True):
        if libelle_ligne.strip() == "":
            st.error("⚠️ Le libellé de la ligne est obligatoire")
        elif debit_ligne == 0 and credit_ligne == 0:
            st.error("⚠️ Veuillez saisir un montant en débit OU en crédit")
        elif debit_ligne > 0 and credit_ligne > 0:
            st.error("⚠️ Une ligne ne peut pas avoir à la fois un débit ET un crédit")
        else:
            st.session_state.operation_en_cours.append({
                'Compte': compte_ligne,
                'Libellé ligne': libelle_ligne,
                'Débit': debit_ligne,
                'Crédit': credit_ligne
            })
            st.rerun()

with col_btn2:
    if len(st.session_state.operation_en_cours) > 0:
        total_debit_op = sum([l['Débit'] for l in st.session_state.operation_en_cours])
        total_credit_op = sum([l['Crédit'] for l in st.session_state.operation_en_cours])
        
        equilibre = abs(total_debit_op - total_credit_op) < 0.01
        
        if st.button("✅ Valider l'opération", 
                    type="primary", 
                    disabled=not equilibre,
                    use_container_width=True):
            
            if not libelle_operation.strip():
                st.error("⚠️ Le libellé de l'opération est obligatoire")
            else:
                # Ajouter toutes les lignes au journal
                for ligne in st.session_state.operation_en_cours:
                    st.session_state.journal.append({
                        "Date": date_operation,
                        "Libellé opération": libelle_operation,
                        "N° Pièce": num_piece,
                        "Compte": ligne['Compte'],
                        "Intitulé compte": PLAN_COMPTABLE[ligne['Compte']],
                        "Libellé ligne": ligne['Libellé ligne'],
                        "Débit": ligne['Débit'],
                        "Crédit": ligne['Crédit']
                    })
                
                # Réinitialiser
                st.session_state.operation_en_cours = []
                
                # Incrémenter le numéro de pièce
                try:
                    num_part = ''.join(filter(str.isdigit, num_piece))
                    text_part = ''.join(filter(str.isalpha, num_piece))
                    if num_part:
                        new_num = int(num_part) + 1
                        st.session_state.num_piece_op = f"{text_part}{new_num:06d}" if text_part else f"OP{new_num:03d}"
                except:
                    pass
                
                st.success("✅ Opération enregistrée dans le journal !")
                st.rerun()

with col_btn3:
    if len(st.session_state.operation_en_cours) > 0:
        if st.button("❌ Annuler l'opération", type="secondary", use_container_width=True):
            st.session_state.operation_en_cours = []
            st.rerun()

# JOURNAL - TOUJOURS VISIBLE
st.header("📖 Journal")

if len(st.session_state.journal) > 0:
    nb_operations = len(set([e['N° Pièce'] for e in st.session_state.journal]))
    nb_ecritures = len(st.session_state.journal)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📝 Écritures saisies", nb_ecritures)
    with col2:
        st.metric("📋 Opérations", nb_operations)
    
    # Grouper par opération pour affichage
    df_journal = pd.DataFrame(st.session_state.journal)
    
    operations = df_journal.groupby('N° Pièce')
    
    for num_piece, group in operations:
        # En-tête opération
        premiere_ligne = group.iloc[0]
        st.markdown(f"**{premiere_ligne['Date']}** - {premiere_ligne['Libellé opération']} - *Pièce {num_piece}*")
        
        # Lignes de l'opération
        for idx, row in group.iterrows():
            col1, col2, col3, col4, col5 = st.columns([1.5, 4, 3, 2, 2])
            
            with col1:
                st.text(row['Compte'])
            with col2:
                st.text(row['Intitulé compte'])
            with col3:
                st.text(row['Libellé ligne'])
            with col4:
                st.text(f"{row['Débit']:.2f} €" if row['Débit'] > 0 else "")
            with col5:
                st.text(f"{row['Crédit']:.2f} €" if row['Crédit'] > 0 else "")
        
        # Vérifier équilibre opération
        total_d = group['Débit'].sum()
        total_c = group['Crédit'].sum()
        
        if abs(total_d - total_c) < 0.01:
            st.success(f"✓ Opération équilibrée : {total_d:.2f} €")
        else:
            st.error(f"✗ Opération déséquilibrée : écart de {abs(total_d - total_c):.2f} €")
        
        st.markdown("---")
    
    total_debit = df_journal['Débit'].sum()
    total_credit = df_journal['Crédit'].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Débit", f"{total_debit:.2f} €")
    with col2:
        st.metric("Total Crédit", f"{total_credit:.2f} €")
    with col3:
        if abs(total_debit - total_credit) < 0.01:
            st.success("✓ JOURNAL ÉQUILIBRÉ")
        else:
            st.error(f"✗ DÉSÉQUILIBRÉ : {abs(total_debit - total_credit):.2f} €")
    
    # BALANCE - SI 2+ ÉCRITURES
    if nb_ecritures >= 2:
        st.header("⚖️ Balance")
        
        balance = df_journal.groupby(['Compte', 'Intitulé compte']).agg({
            'Débit': 'sum',
            'Crédit': 'sum'
        }).reset_index()
        
        balance['Solde Débiteur'] = balance.apply(
            lambda row: row['Débit'] - row['Crédit'] if row['Débit'] > row['Crédit'] else 0, 
            axis=1
        )
        balance['Solde Créditeur'] = balance.apply(
            lambda row: row['Crédit'] - row['Débit'] if row['Crédit'] > row['Débit'] else 0, 
            axis=1
        )
        
        st.dataframe(balance, use_container_width=True, hide_index=True)
        
        total_solde_debiteur = balance['Solde Débiteur'].sum()
        total_solde_crediteur = balance['Solde Créditeur'].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Soldes Débiteurs", f"{total_solde_debiteur:.2f} €")
        with col2:
            st.metric("Total Soldes Créditeurs", f"{total_solde_crediteur:.2f} €")
        with col3:
            if abs(total_solde_debiteur - total_solde_crediteur) < 0.01:
                st.success("✓ BALANCE ÉQUILIBRÉE")
            else:
                st.error(f"✗ DÉSÉQUILIBRÉE : {abs(total_solde_debiteur - total_solde_crediteur):.2f} €")
    
    # GRAND LIVRE
    if nb_ecritures >= 1:
        st.header("📚 Grand Livre")
        
        # Sélection compte
        comptes_utilises = sorted(df_journal['Compte'].unique())
        
        compte_selectionne = st.selectbox(
            "Sélectionnez un compte à afficher",
            options=comptes_utilises,
            format_func=lambda x: f"{x} - {PLAN_COMPTABLE[x]}"
        )
        
        if compte_selectionne:
            st.subheader(f"Compte {compte_selectionne} - {PLAN_COMPTABLE[compte_selectionne]}")
            
            # Filtrer les écritures du compte
            ecritures_compte = df_journal[df_journal['Compte'] == compte_selectionne].copy()
            
            # Calculer le solde progressif
            ecritures_compte['Mouvement Débit'] = ecritures_compte['Débit']
            ecritures_compte['Mouvement Crédit'] = ecritures_compte['Crédit']
            ecritures_compte['Solde'] = (ecritures_compte['Débit'] - ecritures_compte['Crédit']).cumsum()
            
            # Afficher
            colonnes_affichage = ['Date', 'Libellé opération', 'N° Pièce', 'Libellé ligne', 
                                 'Mouvement Débit', 'Mouvement Crédit', 'Solde']
            
            st.dataframe(ecritures_compte[colonnes_affichage], use_container_width=True, hide_index=True)
            
            # Totaux et solde final
            total_debit_compte = ecritures_compte['Débit'].sum()
            total_credit_compte = ecritures_compte['Crédit'].sum()
            solde_final = total_debit_compte - total_credit_compte
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Débit", f"{total_debit_compte:.2f} €")
            with col2:
                st.metric("Total Crédit", f"{total_credit_compte:.2f} €")
            with col3:
                if solde_final >= 0:
                    st.metric("Solde final", f"{solde_final:.2f} €", help="Solde débiteur")
                else:
                    st.metric("Solde final", f"{abs(solde_final):.2f} €", delta="Créditeur", help="Solde créditeur")
    
    # COMPTE DE RÉSULTAT - SI AU MOINS 1 CHARGE OU 1 PRODUIT
    has_charges = any(e['Compte'] in COMPTES_CHARGES for e in st.session_state.journal)
    has_produits = any(e['Compte'] in COMPTES_PRODUITS for e in st.session_state.journal)
    
    if has_charges or has_produits:
        st.header("💰 Compte de résultat")
        
        charges = df_journal[df_journal['Compte'].isin(COMPTES_CHARGES)].groupby(['Compte', 'Intitulé compte']).agg({
            'Débit': 'sum'
        }).reset_index()
        charges.columns = ['Compte', 'Intitulé', 'Montant']
        
        produits = df_journal[df_journal['Compte'].isin(COMPTES_PRODUITS)].groupby(['Compte', 'Intitulé compte']).agg({
            'Crédit': 'sum'
        }).reset_index()
        produits.columns = ['Compte', 'Intitulé', 'Montant']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("CHARGES")
            if len(charges) > 0:
                st.dataframe(charges, use_container_width=True, hide_index=True)
                total_charges = charges['Montant'].sum()
                st.metric("Total Charges", f"{total_charges:.2f} €")
            else:
                st.info("Aucune charge enregistrée")
                total_charges = 0
        
        with col2:
            st.subheader("PRODUITS")
            if len(produits) > 0:
                st.dataframe(produits, use_container_width=True, hide_index=True)
                total_produits = produits['Montant'].sum()
                st.metric("Total Produits", f"{total_produits:.2f} €")
            else:
                st.info("Aucun produit enregistré")
                total_produits = 0
        
        resultat = total_produits - total_charges
        
        st.markdown("---")
        if resultat >= 0:
            st.success(f"✅ RÉSULTAT : BÉNÉFICE de {resultat:.2f} €")
        else:
            st.error(f"❌ RÉSULTAT : PERTE de {abs(resultat):.2f} €")
    else:
        resultat = 0
    
    # BILAN - SI AU MOINS 1 COMPTE ACTIF ET 1 COMPTE PASSIF
    has_actif = any(e['Compte'] in COMPTES_ACTIF for e in st.session_state.journal)
    has_passif = any(e['Compte'] in COMPTES_PASSIF for e in st.session_state.journal)
    
    if has_actif and has_passif and nb_ecritures >= 2:
        st.header("📊 Bilan simplifié")
        
        actif = balance[balance['Compte'].isin(COMPTES_ACTIF)][['Compte', 'Intitulé compte', 'Solde Débiteur']].copy()
        actif.columns = ['Compte', 'Intitulé', 'Montant']
        actif = actif[actif['Montant'] > 0]
        
        # Soustraire les amortissements
        amortissements = balance[balance['Compte'].isin(COMPTES_AMORTISSEMENTS)][['Compte', 'Intitulé compte', 'Solde Créditeur']].copy()
        if len(amortissements) > 0:
            amortissements.columns = ['Compte', 'Intitulé', 'Montant']
            amortissements['Montant'] = -amortissements['Montant']
            actif = pd.concat([actif, amortissements], ignore_index=True)
        
        passif = balance[balance['Compte'].isin(COMPTES_PASSIF)][['Compte', 'Intitulé compte', 'Solde Créditeur']].copy()
        passif.columns = ['Compte', 'Intitulé', 'Montant']
        passif = passif[passif['Montant'] > 0]
        
        # Ajouter le résultat
        if resultat >= 0:
            passif = pd.concat([passif, pd.DataFrame({
                'Compte': ['RÉSULTAT'],
                'Intitulé': ['Bénéfice de l\'exercice'],
                'Montant': [resultat]
            })], ignore_index=True)
        else:
            actif = pd.concat([actif, pd.DataFrame({
                'Compte': ['RÉSULTAT'],
                'Intitulé': ['Perte de l\'exercice'],
                'Montant': [abs(resultat)]
            })], ignore_index=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("ACTIF")
            if len(actif) > 0:
                st.dataframe(actif, use_container_width=True, hide_index=True)
                total_actif = actif['Montant'].sum()
                st.metric("Total Actif", f"{total_actif:.2f} €")
            else:
                st.info("Aucun actif enregistré")
                total_actif = 0
        
        with col2:
            st.subheader("PASSIF")
            if len(passif) > 0:
                st.dataframe(passif, use_container_width=True, hide_index=True)
                total_passif = passif['Montant'].sum()
                st.metric("Total Passif", f"{total_passif:.2f} €")
            else:
                st.info("Aucun passif enregistré")
                total_passif = 0
        
        st.markdown("---")
        if abs(total_actif - total_passif) < 0.01:
            st.success(f"✅ BILAN ÉQUILIBRÉ : {total_actif:.2f} €")
        else:
            st.error(f"❌ BILAN DÉSÉQUILIBRÉ : Écart de {abs(total_actif - total_passif):.2f} €")
    
    # BOUTON EFFACER TOUT
    st.markdown("---")
    if st.button("🗑️ Effacer tout le journal", type="secondary"):
        st.session_state.journal = []
        st.session_state.operation_en_cours = []
        st.rerun()
    
    # EXPORT
    st.header("📥 Export des résultats")
    
    if nom_eleve:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Info
            info_sheet = pd.DataFrame({
                'Information': ['Nom élève', 'Date export', 'Nb écritures', 'Nb opérations'],
                'Valeur': [nom_eleve, datetime.now().strftime("%d/%m/%Y %H:%M"), nb_ecritures, nb_operations]
            })
            info_sheet.to_excel(writer, sheet_name='Informations', index=False)
            
            # Journal
            df_journal.to_excel(writer, sheet_name='Journal', index=False)
            
            # Balance (si existe)
            if nb_ecritures >= 2:
                balance.to_excel(writer, sheet_name='Balance', index=False)
            
            # CR (si existe)
            if has_charges or has_produits:
                compte_resultat = pd.DataFrame({
                    'Type': ['CHARGES'] * len(charges) + ['TOTAL CHARGES', ''] + ['PRODUITS'] * len(produits) + ['TOTAL PRODUITS', '', 'RÉSULTAT'],
                    'Compte': list(charges['Compte']) + ['', ''] + list(produits['Compte']) + ['', '', ''],
                    'Intitulé': list(charges['Intitulé']) + ['', ''] + list(produits['Intitulé']) + ['', '', 'Bénéfice' if resultat >= 0 else 'Perte'],
                    'Montant': list(charges['Montant']) + [total_charges, 0] + list(produits['Montant']) + [total_produits, 0, abs(resultat)]
                })
                compte_resultat.to_excel(writer, sheet_name='Compte de résultat', index=False)
            
            # Bilan (si existe)
            if has_actif and has_passif and nb_ecritures >= 2:
                max_len = max(len(actif), len(passif))
                
                actif_pad = actif.copy()
                while len(actif_pad) < max_len:
                    actif_pad = pd.concat([actif_pad, pd.DataFrame({'Compte': [''], 'Intitulé': [''], 'Montant': [0]})], ignore_index=True)
                
                passif_pad = passif.copy()
                while len(passif_pad) < max_len:
                    passif_pad = pd.concat([passif_pad, pd.DataFrame({'Compte': [''], 'Intitulé': [''], 'Montant': [0]})], ignore_index=True)
                
                bilan_df = pd.DataFrame({
                    'ACTIF_Compte': list(actif_pad['Compte']) + ['', 'TOTAL'],
                    'ACTIF_Intitulé': list(actif_pad['Intitulé']) + ['', ''],
                    'ACTIF_Montant': list(actif_pad['Montant']) + [0, total_actif],
                    'PASSIF_Compte': list(passif_pad['Compte']) + ['', 'TOTAL'],
                    'PASSIF_Intitulé': list(passif_pad['Intitulé']) + ['', ''],
                    'PASSIF_Montant': list(passif_pad['Montant']) + [0, total_passif]
                })
                bilan_df.to_excel(writer, sheet_name='Bilan', index=False)
        
        output.seek(0)
        
        date_export = datetime.now().strftime("%Y%m%d_%H%M")
        nom_fichier = f"{nom_eleve.replace(' ', '_')}_Bodega_{date_export}.xlsx"
        
        st.download_button(
            label="📥 Télécharger mon travail (Excel)",
            data=output,
            file_name=nom_fichier,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
    else:
        st.warning("⚠️ Veuillez saisir votre nom en haut de la page pour télécharger")
    
else:
    st.info("👆 Commencez par saisir une opération comptable ci-dessus")
    st.markdown("""
    **Guide rapide :**
    1. Remplissez les informations de l'opération (Date, Libellé, N° Pièce)
    2. Ajoutez les lignes comptables une par une
    3. Validez l'opération quand Débit = Crédit
    4. Consultez le Journal, la Balance, le Grand Livre, le Compte de résultat et le Bilan
    """)
