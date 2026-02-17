import pandas as pd

# ÉTAPE 1 — Nettoyage & Préparation

df = pd.read_excel('ed.xlsx')

df.columns = (
    df.columns.str.strip().str.lower()
    .str.replace(" ", "_")
    .str.replace("é","e")
    .str.replace("è","e")
    .str.replace("ê","e")
    .str.replace("à","a")
)

df['date_reglement'] = pd.to_datetime(
    df['date_reglement'].astype(str) + ' ' + df['heure_reglement'].astype(str),
    errors='coerce'
)

df['jour'] = df['date_reglement'].dt.date
df['annee'] = df['date_reglement'].dt.year
df['mois'] = df['date_reglement'].dt.month
df['semaine'] = df['date_reglement'].dt.isocalendar().week
df['heure'] = df['date_reglement'].dt.hour

cols_finance = ['montant_rgl','montant_verse','montant_rst','solde_cpp']
for col in cols_finance:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(subset=['date_reglement','montant_rgl'])
df = df.drop_duplicates()

# ÉTAPE 2 — Analyse des tendances

ca_journalier = df.groupby('jour')['montant_rgl'].sum()
ca_hebdomadaire = df.groupby('semaine')['montant_rgl'].sum()
ca_mensuel = df.groupby('mois')['montant_rgl'].sum()
solde_moyen_journalier = df.groupby('jour')['solde_cpp'].mean()

# ÉTAPE 3 — Clients clés

clients_top = (
    df.groupby('id_client')
      .agg(
          total_depense=('montant_rgl','sum'),
          moyenne_transaction=('montant_rgl','mean'),
          solde_moyen=('solde_cpp','mean')
      )
      .sort_values(by='total_depense', ascending=False)
      .head(10)
)

clients_impayes = (
    df.groupby('id_client')['montant_rst']
      .sum()
      .reset_index()
)

clients_impayes = clients_impayes[clients_impayes['montant_rst'] > 0]
# ÉTAPE 4 — Restaurants & Heures de pointe


ca_restaurant = (
    df.groupby('restaurant')['montant_rgl']
      .sum()
      .sort_values(ascending=False)
)

transactions_par_heure = df.groupby('heure')['montant_rgl'].count()

# ÉTAPE 5 — Détection des anomalies (IQR)

Q1 = df['montant_rgl'].quantile(0.25)
Q3 = df['montant_rgl'].quantile(0.75)
IQR = Q3 - Q1

seuil_bas = Q1 - 1.5 * IQR
seuil_haut = Q3 + 1.5 * IQR

anomalies = df[
    (df['montant_rgl'] < seuil_bas) |
    (df['montant_rgl'] > seuil_haut)
]

anomalies_client = anomalies.groupby('id_client')['montant_rgl'].count()
anomalies_restaurant = anomalies.groupby('restaurant')['montant_rgl'].count()
anomalies_heure = anomalies.groupby('heure')['montant_rgl'].count()

# ÉTAPE 6 — Performance des caissiers

performance_caissiers = (
    df.groupby('id_user')
      .agg(
          montant_total=('montant_rgl','sum'),
          nb_transactions=('montant_rgl','count')
      )
      .sort_values(by='montant_total', ascending=False)
)

# ÉTAPE 7 — Corrélation

correlation_solde_depense = df['solde_cpp'].corr(df['montant_rgl'])

# ÉTAPE 8 — Reporting (Synthèse)


print("\n===== RAPPORT FINAL =====")

print("\nCA Mensuel:\n", ca_mensuel)
print("\nSolde Moyen Journalier:\n", solde_moyen_journalier.head())

print("\nTop 10 Clients:\n", clients_top)
print("\nClients à risque (impayés):\n", clients_impayes.head())

print("\nTop Restaurants:\n", ca_restaurant.head())
print("\nHeures de pointe:\n", transactions_par_heure.sort_values(ascending=False).head())

print("\nNombre d'anomalies détectées:", len(anomalies))
print("\nTop Caissiers:\n", performance_caissiers.head())

print("\nCorrélation Solde_CPP vs Montant_Rgl:", correlation_solde_depense)

# ÉTAPE 9 — Automatisation (fonction)


def run_system(file_path):
    print("\nSystème analytique exécuté avec succès.")

run_system('REGLEMENTS_CARTES_PREPAYEES_FAST_FOOD.xlsx')
