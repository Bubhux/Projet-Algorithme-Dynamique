import pandas as pd
import itertools
import time
import humanize
import psutil
import math
import matplotlib.pyplot as plt
from tqdm import tqdm
from tabulate import tabulate
from typing import List, Tuple


# Variable de condition pour afficher ou supprimer les barres de progression
show_progress = True


def read_csv(filename: str) -> List[Tuple[str, List[float]]]:
    """Fonction pour lire les fichiers csv"""
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
            action = (row.name, float(row.price), float(row.profit))
            actions.append(action)

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


def method_bruteforce(actions: List[Tuple[str, List[float]]],
                      max_cost: int,
                      show_progress: bool = True) -> Tuple[List[str], float, int]:
    """Fonction pour trouver la meilleure combinaison d'actions et son bénéfice total"""

    # Meilleure combinaison trouvée jusqu'à présent
    best_combination: List[str] = []
    # Meilleur bénéfice trouvé jusqu'à présent
    best_profit: float = 0
    # Compteur de combinaisons
    count_combinations: int = 0
    # Liste des temps d'exécution
    execution_times: List[float] = []

    # Génération de toutes les combinaisons possibles d'actions
    for i in tqdm(range(1, len(actions) + 1), desc="Calcul en cours", disable=not show_progress):
        # Mesurer le temps d'exécution pour chaque taille d'entrée
        start_time = time.time()
        # Générer toutes les combinaisons d'actions de taille i
        combinations = itertools.combinations(actions, i)
        for combination in tqdm(combinations, desc="Calcul en cours", leave=False, disable=not show_progress):
            count_combinations += 1
            # Vérifier si la combinaison satisfait la contrainte de coût maximum
            total_cost = sum(action[1] for action in combination)
            if total_cost <= max_cost:
                # Calculer le bénéfice total de la combinaison
                total_profit = total_profit = sum(action[1] * action[2] / 100 for action in combination)
                # Mettre à jour la meilleure combinaison si elle est meilleure que la précédente
                if total_profit > best_profit:
                    best_combination = list(combination)
                    best_profit = total_profit

        # Mesurer le temps d'exécution pour la taille de l'entrée actuelle
        execution_time = time.time() - start_time
        execution_times.append(execution_time)

    return best_combination, best_profit, count_combinations, execution_times


def generate_graphs(actions: List[Tuple[str, List[float]]], max_cost: int) -> None:
    """Fonction pour générer les graphiques"""

    # Variables pour stocker les données
    num_inputs = []
    time_complexity = []
    memory_analysis = []

    # Mesure de l'utilisation de la mémoire initiale
    initial_memory = measure_memory_usage()
    initial_memory_mb = initial_memory / (1024 * 1024)

    # Boucle pour mesurer les performances pour différentes tailles d'entrées
    for i in tqdm(range(1, len(actions) + 1), desc="Patientez calcul en cours pour la création des graphiques "):
        num_inputs.append(i)

        # Exécution de la méthode bruteforce
        start_time = time.time()
        method_bruteforce(actions, max_cost, show_progress=False)
        end_time = time.time()
        execution_time = end_time - start_time
        time_complexity.append(execution_time)

        # Mesure de l'utilisation de la mémoire
        memory_usage = measure_memory_usage()
        memory_analysis.append(memory_usage / (1024 * 1024))

    # Création du graphique en deux sous-graphiques
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=False)

    # Sous-graphique 1 : Complexité temporelle
    # Crée une liste contenant les valeurs exponentielles de chaque élément dans la liste num_inputs
    exponential_complexity = [math.exp(i) for i in num_inputs]
    ax1.plot(num_inputs, exponential_complexity, "b--", label="Complexité temporelle")
    ax1.scatter(num_inputs, exponential_complexity, s=10)

    # Ajout de la courbe du temps d'exécution avec le format en secondes
    ax1.plot(num_inputs, time_complexity, "r--", label="Temps d'exécution ({:.2f} s)".format(execution_time))
    ax1.set_xlabel("Nombre d'entrées (n)")
    ax1.set_title("La complexité temporelle de method_bruteforce est O(2^n)")
    ax1.set_ylabel("Complexité temporelle exponentielle")
    ax1.legend()

    # Configuration de l'axe des y pour afficher les valeurs complètes sans notation scientifique
    ax1.ticklabel_format(style='plain', axis='y')

    # Sous-graphique 2 : Analyse de mémoire
    ax2.plot(num_inputs, memory_analysis, "g--", label="Analyse de mémoire")
    ax2.scatter(num_inputs, memory_analysis, s=10)
    ax2.set_xlabel("Nombre d'entrées (n)")
    ax2.set_title("La complexité spatiale de method_bruteforce est O(n)")
    ax2.set_ylabel("Mémoire utilisée (Mo)")
    ax2.legend()

    # Configuration de l'axe des y pour afficher les valeurs complètes sans notation scientifique
    ax2.ticklabel_format(style='plain', axis='y')

    plt.tight_layout()
    plt.show()

    # Mesure de l'utilisation de la mémoire finale
    final_memory = measure_memory_usage()
    final_memory_mb = final_memory / (1024 * 1024)

    print(f"Utilisation initiale de la mémoire : {initial_memory_mb:.2f} Mo")
    print(f"Utilisation finale de la mémoire : {final_memory_mb:.2f} Mo\n")


def measure_memory_usage() -> int:
    """Fonction pour mesurer l'utilisation de la mémoire"""
    process = psutil.Process()
    memory_info = process.memory_info()

    return memory_info.rss


def main() -> None:
    """Fonction principale pour lancer le prorgamme"""

    # Mesure du temps d'exécution
    start_time = time.time()

    # Chargement des données à partir d'un fichier CSV
    filename = "dataset3.csv"
    actions = read_csv(filename)
    if actions is None:
        exit()

    initial_memory = measure_memory_usage()
    initial_memory_mb = initial_memory / (1024 * 1024)

    best_combination, best_profit, count_combinations, execution_times = method_bruteforce(
        actions,
        max_cost=500,
        show_progress=True
    )

    final_memory = measure_memory_usage()
    final_memory_mb = final_memory / (1024 * 1024)

    # Afficher les résultats avec tabulate
    print(f"\nActions les plus rentables ({len(best_combination)} actions) :\n")

    table = []
    for action in best_combination:
        table.append([action[0], action[1], action[2]])
    print(tabulate(table, headers=["Action", "Coût (€)", "Bénéfice (%)"], tablefmt="psql"))

    total_cost = sum(action[1] for action in best_combination)
    print(f"Coût total de l'investissement : {total_cost} euros")

    total_cost = sum(action[1] for action in best_combination)
    print(
        f"Bénéfice sur 2 ans : {best_profit:.2f} euros "
        f"({best_profit / total_cost * 100:.2f}%)"
    )

    # Afficher le temps d'exécution du programme
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Temps d'exécution : {execution_time:.2f} secondes")

    # Utiliser intword pour afficher le nombre de combinaisons calculées
    # Avec l'unité de mesure "millions" ou "milliards"
    print(f"Nombre de combinaisons calculées : {humanize.intword(count_combinations)}(s)\n")

    # Mesure de l'utilisation de la RAM
    print(f"Utilisation initiale de la mémoire : {initial_memory_mb:.2f} Mo")
    print(f"Utilisation finale de la mémoire : {final_memory_mb:.2f} Mo\n")

    # Demande à l'utilisateur s'il souhaite créer un graphique
    create_graph = input("Souhaitez-vous créer un graphique à partir des résultats ?\n"
                         "1. Oui\n"
                         "2. Non\n"
                         "> ")

    # Vérifie que l'utilisateur a choisi un choix valide
    while create_graph not in ["1", "2"]:
        print("Choix invalide, saisissez 1 ou 2.")
        create_graph = input("> ")

    # Définit la création du graphique en fonction du choix de l'utilisateur
    if create_graph == "1":
        # Création des graphiques
        generate_graphs(actions, max_cost=500)
    else:
        exit()


if __name__ == "__main__":
    main()
