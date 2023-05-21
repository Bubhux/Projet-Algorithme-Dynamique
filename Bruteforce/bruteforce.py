import pandas as pd
import itertools
import time
import humanize
import psutil
from tqdm import tqdm
from tabulate import tabulate
from typing import Dict, Optional


def read_csv(filename: str) -> Optional[Dict[str, Dict[str, float]]]:
    """Fonction pour lire les fichiers csv"""

    try:
        # Lecture du fichier CSV
        df = pd.read_csv(filename)

        # Vérification des colonnes requises
        required_columns = ['name', 'price', 'profit']
        if not set(required_columns).issubset(df.columns):
            print(f"Erreur : le fichier CSV ne contient pas les colonnes requises : {required_columns}")
            return None

        # Création d'un dictionnaire contenant les actions
        actions = {}
        for row in df.itertuples(index=False):
            actions[row.name] = {
                "price": float(row.price),
                "profit": float(row.profit)
            }

        # Affichage du tableau
        for index, row in df.iterrows():
            df['price (€)'] = df['price'].apply(lambda x: '{:.2f} €'.format(x))
            df['profit (%)'] = df['profit'].apply(lambda x: '{:.2f} %'.format(x))

        return actions

    except FileNotFoundError:
        print(f"Erreur : le fichier CSV '{filename}' est introuvable.")
        return None
    except pd.errors.EmptyDataError:
        print(f"Erreur : le fichier CSV '{filename}' est vide.")
        return None
    except pd.errors.ParserError:
        print(f"Erreur : impossible de parser le fichier CSV '{filename}'.")
        return None

# Mesure de l'utilisation de la RAM avant l'exécution de la fonction
process = psutil.Process()
memory_before = process.memory_info().rss / 1024 / 1024

# Définition des contraintes
max_cost = 500

# Chargement des données à partir d'un fichier CSV
filename = "dataset3.csv"
actions = read_csv(filename)
if actions is None:
    exit()

# Définition des variables pour stocker la meilleure combinaison d'actions et son bénéfice total
best_combination = []
best_profit = 0

# Mesure du temps d'exécution
start_time = time.time()
count_combinations = 0

# Génération de toutes les combinaisons possibles d'actions
for i in tqdm(range(1, len(actions) + 1), desc="Calcul en cours"):
    for combination in tqdm(itertools.combinations(actions.keys(), i), desc="Calcul en cours", leave=False):
        count_combinations += 1
        # Vérification si la combinaison satisfait la contrainte de coût maximum
        total_cost = sum(actions[action]["price"] for action in combination)
        if total_cost <= max_cost:
            # Calcul du bénéfice total de la combinaison
            total_profit = sum(actions[action]["price"] * actions[action]["profit"] / 100 for action in combination)
            # Mise à jour de la meilleure combinaison si elle est meilleure que la précédente
            if total_profit > best_profit:
                best_combination = list(combination)
                best_profit = total_profit

# Afficher les résultats avec tabulate
print(f"\nActions les plus rentables ({len(best_combination)} actions) :\n")

table = []
for action in best_combination:
    table.append([action, actions[action]['price'], actions[action]['profit']])
print(tabulate(table, headers=["Action", "Coût (€)", "Bénéfice (%)"], tablefmt="psql"))
print(f"Coût total de l'investissement : {sum(actions[action]['price'] for action in best_combination)} euros")
print(f"Bénéfice sur 2 ans : {best_profit:.2f} euros ({best_profit/sum(actions[action]['price'] for action in best_combination)*100:.2f}%)")

# Afficher le temps d'exécution du programme
end_time = time.time()
execution_time = end_time - start_time
print(f"Temps d'exécution : {execution_time:.2f} secondes")

# Utiliser intword pour afficher le nombre de combinaisons calculées avec l'unité de mesure "millions" ou "milliards"
print(f"Nombre de combinaisons calculées : {humanize.intword(count_combinations)}(s)")

# Mesure de l'utilisation de la RAM après l'exécution de la fonction
memory_after = process.memory_info().rss / 1024 / 1024
print(f"RAM utilisée : {memory_after - memory_before:.2f} Mo")
