import pandas as pd
import itertools
import time
import humanize
import psutil
import math
import click
from rich.console import Console
from rich.table import Table
import matplotlib.pyplot as plt
from tqdm import tqdm

from typing import List, Tuple


# Variable de condition pour afficher ou supprimer les barres de progression
show_progress = True
console = Console()


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
                total_profit = sum(action[1] * action[2] / 100 for action in combination)
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


@click.command()
def main() -> None:
    """Fonction principale pour lancer le programme"""

    # Affichage des options de fichiers disponibles
    console.print()
    console.print("Choisissez un fichier :", style="bold blue")
    console.print("1. dataset1.csv (1000 actions)")
    console.print("2. dataset2.csv (1000 actions)")
    console.print("3. dataset3.csv (20 actions). ", end="")
    console.print("Par défaut le fichier dataset3.csv sera utilisé.", style="bold red")
    choice = click.prompt("> ", type=click.Choice(["1", "2", "3"]), default="3", show_default=False)

    # Mappage des choix de l'utilisateur vers les noms de fichiers correspondants
    filenames = {
        "1": "dataset1.csv",
        "2": "dataset2.csv",
        "3": "dataset3.csv",
    }
    filename = filenames[choice]

    # Demande à l'utilisateur le montant maximal à investir
    max_invest_input = click.prompt(
        "Entrez le montant maximal à investir (500€ par défaut)",
        default=500,
        type=float,
    )

    # Mesure du temps d'exécution
    start_time = time.time()

    # Chargement des données à partir d'un fichier CSV
    actions = read_csv(filename)
    if actions is None:
        exit()

    initial_memory = measure_memory_usage()
    initial_memory_mb = initial_memory / (1024 * 1024)

    best_combination, best_profit, count_combinations, execution_times = method_bruteforce(
        actions,
        max_cost=max_invest_input,
        show_progress=True
    )

    final_memory = measure_memory_usage()
    final_memory_mb = final_memory / (1024 * 1024)

    # Afficher les résultats avec rich
    console.print("\n[b]Actions les plus rentables[/b] ([cyan]" + str(len(best_combination)) + "[/cyan] actions) :")

    table = Table(title="Résultats")
    table.add_column("Action", style="cyan")
    table.add_column("Coût (€)", style="magenta")
    table.add_column("Bénéfice (%)", style="green")

    for action in best_combination:
        table.add_row(action[0], str(action[1]), "{:.2f}".format(action[2]))

    console.print(table)
    total_cost = sum(action[1] for action in best_combination)
    console.print(f"Extraction du fichier {filename}\n", style="bold blue")
    console.print(f"Coût total de l'investissement : [bold]{total_cost}[/bold] euros")

    console.print(
        f"Bénéfice sur 2 ans : [bold]{best_profit:.2f}[/bold] euros "
        f"([bold]{best_profit / total_cost * 100:.2f}[/bold]%)"
    )

    # Afficher le temps d'exécution du programme
    end_time = time.time()
    execution_time = end_time - start_time
    console.print(f"Temps d'exécution : [bold]{execution_time:.2f}[/bold] secondes")

    # Utiliser intword pour afficher le nombre de combinaisons calculées
    # Avec l'unité de mesure "millions" ou "milliards"
    console.print(f"Nombre de combinaisons calculées : [bold]{humanize.intword(count_combinations)}[/bold](s)\n")

    # Mesure de l'utilisation de la RAM
    console.print(f"Utilisation initiale de la mémoire : [bold]{initial_memory_mb:.2f}[/bold] Mo")
    console.print(f"Utilisation finale de la mémoire : [bold]{final_memory_mb:.2f}[/bold] Mo\n")

    # Demande à l'utilisateur s'il souhaite créer un graphique
    if click.confirm("Souhaitez-vous créer un graphique à partir des résultats ?"):
        # Création des graphiques
        generate_graphs(actions, max_cost=max_invest_input)
    else:
        exit()


if __name__ == "__main__":
    main()
