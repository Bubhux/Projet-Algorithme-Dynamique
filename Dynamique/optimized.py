import pandas as pd
import time
import humanize
import psutil
from tqdm import tqdm
from tabulate import tabulate
from typing import List, Tuple


def read_csv(filename: str) -> List[Tuple[str, int, float]]:

    try:
        # Lecture du fichier CSV
        df = pd.read_csv(filename)

        # Vérification des colonnes requises
        required_columns = ['name', 'price', 'profit']
        if not set(required_columns).issubset(df.columns):
            print(f"Erreur : le fichier CSV ne contient pas les colonnes requises : {required_columns}")
            return None

        # Création d'une liste contenant les actions
        actions = []
        for row in df.itertuples(index=False):
            if float(row.price) <= 0 or float(row.profit) <= 0:
                pass
            else:
                action = (
                    row.name,
                    int(float(row.price)*100),
                    float(float(row.price) * float(row.profit) / 100)
                )
                actions.append(action)

        # Affichage du tableau
        for index, row in df.iterrows():
            df['price (€)'] = df['price'].apply(lambda x: '{:.2f} €'.format(x))
            df['profit (%)'] = df['profit'].apply(lambda x: '{:.2f} %'.format(x))
        #print(tabulate(df[['name', 'price (€)', 'profit (%)']], headers='keys', tablefmt='psql'))

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

def knapsack_dynamic(actions_list: List[Tuple[str, int, float]], max_invest: float) -> Tuple[List[Tuple[str, int, float]], int]:
    
    # Convertir le budget maximal en centimes
    budjet_max = int(max_invest * 100)

    # Initialiser les listes de prix et de profits
    actions = len(actions_list)
    price = []
    profit = []

    # Extraire les prix et profits de la liste d'actions
    for action in actions_list:
        price.append(action[1])
        profit.append(action[2])

    # Initialiser la matrice
    matrix = [[0 for x in range(budjet_max + 1)] for x in range(actions + 1)]

    # Calculer la matrice
    count_combinations = 0
    for i in tqdm(range(1, actions + 1), desc="Calcul en cours"):
        for w in range(1, budjet_max + 1):
            count_combinations += 1
            if price[i-1] <= w:
                matrix[i][w] = max(profit[i-1] + matrix[i-1][w-price[i-1]], matrix[i-1][w])
            else:
                matrix[i][w] = matrix[i-1][w]

    # Sélectionner les éléments à ajouter dans le portefeuille
    selected_elements = []
    i = budjet_max
    w = actions
    while i >= 0 and w >= 0:
        if matrix[w][i] == matrix[w-1][i - price[w-1]] + profit[w-1]:
            selected_elements.append(actions_list[w-1])
            i -= price[w-1]

        w -= 1
    
    # Retourner la liste d'éléments sélectionnés
    return selected_elements, count_combinations

def measure_memory_usage():
    process = psutil.Process()
    mem_info = process.memory_info()
    
    return mem_info.rss

def main() -> None:

    # Mesure de l'utilisation de la RAM avant l'exécution de la fonction
    #process = psutil.Process()
    #memory_before = process.memory_info().rss / 1024 / 1024

    # Demande à l'utilisateur de choisir un fichier
    choice = input("Choisissez un fichier :\n"
                      "1. dataset1.csv\n"
                      "2. dataset2.csv\n"
                      "3. dataset3.csv\n"
                      "> ")

    # Vérifie que l'utilisateur a choisi un choix valide
    while choice not in ["1", "2", "3"]:
        print("Choix invalide, saisissez 1 ou 2 ou 3.")
        choice = input("> ")

    # Définit le nom du fichier en fonction du choix de l'utilisateur
    if choice == "1":
        filename = "dataset1.csv"
    elif choice == "2":
        filename = "dataset2.csv"
    else:
        filename = "dataset3.csv"

    # Demander à l'utilisateur le montant maximal à investir
    print("Si vous souhaitez choisir un montant différent de 500€.")
    max_invest_input = (
        input("Entrez le montant maximal à investir, "
              "sinon appuyer sur entrée le montant par défaut sera choisi. \n> ")
    )

    # Si l'utilisateur a entré un montant, vérifier qu'il est valide
    if max_invest_input:
        max_invest = float(max_invest_input)
        # Vérifier que max_invest est un nombre valide
        if not isinstance(max_invest, (int, float)):
            print("Le montant entré n'est pas un nombre valide.")
            return
    else:
        max_invest = 500

    # Lecture du fichier CSV
    actions_list = read_csv(filename)

    # Vérifier si la liste d'actions est vide
    if not actions_list:
        return

    # Mesure du temps d'exécution
    start_time = time.time()

    initial_memory = measure_memory_usage()
    initial_memory_mb = initial_memory / (1024 * 1024)
    #print(f"Utilisation initiale de la mémoire : {initial_memory_mb:.2f} MB")
    #print("Initial memory usage: {:.2f} MB".format(initial_memory_mb))

    # Appel de la fonction knapsack_dynamic avec la liste d'actions et le budget maximal
    selected_elements, count_combinations = knapsack_dynamic(actions_list, max_invest)

    final_memory = measure_memory_usage()
    final_memory_mb = final_memory / (1024 * 1024)
    #print(f"Utilisation finale de la mémoire : {final_memory_mb:.2f} MB")
    #print("Final memory usage: ", final_memory_mb, "MB")

    memory_usage = final_memory - initial_memory
    memory_usage_mb = memory_usage / (1024 * 1024)
    #print("Memory usage during function execution: ", memory_usage_mb, "MB")
    #print(f"Utilisation de la mémoire pendant l'exécution de la fonction : {memory_usage_mb:.2f} MB")

    # Afficher les résultats
    print(f"\nActions les plus rentables ({len(selected_elements)} actions) :\n")

    price_total = []
    profit_total = []

    for action in selected_elements:
        price_total.append(action[1] / 100)
        profit_total.append(action[2])

    print(tabulate(
                [(action[0], '{:.2f}'.format(action[1]/100), '{:.2f}'.format(action[2])) 
                for action in selected_elements], 
                    headers=["Action", "Coût (€)", "Bénéfice (%)"], 
                    tablefmt='psql'
    ))

    print(f"Extraction du fichier {filename}\n")
    print(f"Coût total de l'investissement : {sum(price_total)} €")
    print(f"Bénéfice total sur 2 ans : {sum(profit_total):.2f} €")
    print(f"Bénéfice total sur 2 ans en pourcentage : {((sum(profit_total)/sum(price_total))*100):.2f}%")
    print(f"Temps d'exécution : {time.time() - start_time:.2f} secondes")
    
    # Utiliser intword pour afficher le nombre de combinaisons calculées avec l'unité de mesure "millions" ou "milliards"
    print(f"Nombre de combinaisons calculées : {humanize.intword(count_combinations)}(s)\n")

    # Mesure de l'utilisation de la RAM après l'exécution de la fonction
    #memory_after = process.memory_info().rss / 1024 / 1024
    #print(f"RAM utilisée : {memory_after - memory_before:.2f} Mo")

    print(f"Utilisation initiale de la mémoire : {initial_memory_mb:.2f} Mo")
    print(f"Utilisation finale de la mémoire : {final_memory_mb:.2f} Mo")
    #print(f"Utilisation de la mémoire pendant l'exécution de la fonction : {memory_usage_mb:.2f} Mo")


if __name__ == "__main__":
    main()
