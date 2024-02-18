import pandas as pd
import time
import humanize
import psutil
import matplotlib.pyplot as plt
import click
from rich.console import Console
from rich.table import Table
from tqdm import tqdm
from typing import List, Tuple


console = Console()


def read_csv(filename: str) -> List[Tuple[str, int, float]]:
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


def algorithm_dynamic(actions_list: List[Tuple[str, int, float]],
                      max_invest: float,
                      show_progress: bool = True) -> Tuple[List[Tuple[str, int, float]], int]:
    """Fonction algorithme dynamique"""

    # Convertir le budget maximal en centimes
    budjet_max = int(max_invest * 100)

    # Initialiser les listes de prix et de profits
    actions: int = len(actions_list)
    price: List[int] = []
    profit: List[float] = []

    # Extraire les prix et profits de la liste d'actions
    for action in actions_list:
        price.append(action[1])
        profit.append(action[2])

    # Initialiser la matrice
    matrix: List[List[int]] = [[0 for x in range(budjet_max + 1)] for x in range(actions + 1)]

    count_combinations: int = 0
    if show_progress:
        # Afficher une barre de progression si show_progress est True
        progress_bar = tqdm(total=actions, desc="Calcul en cours ")

    # Calculer la matrice
    for i in range(1, actions + 1):
        for w in range(1, budjet_max + 1):
            count_combinations += 1
            if price[i-1] <= w:
                # Choix entre prendre l'action ou ne pas la prendre
                matrix[i][w] = max(profit[i-1] + matrix[i-1][w-price[i-1]], matrix[i-1][w])
            else:
                # Ne pas prendre l'action si son prix est supérieur au budget disponible
                matrix[i][w] = matrix[i-1][w]

        if show_progress:
            # Mettre à jour la barre de progression si show_progress est True
            progress_bar.update(1)

    if show_progress:
        # Fermer la barre de progression si show_progress est True
        progress_bar.close()

    # Sélectionner les éléments à ajouter dans le portefeuille
    selected_elements: List[Tuple[str, int, float]] = []
    i: int = budjet_max
    w: int = actions
    while i >= 0 and w >= 0:
        if matrix[w][i] == matrix[w-1][i - price[w-1]] + profit[w-1]:
            # Ajouter l'action sélectionnée dans la liste des éléments sélectionnés
            selected_elements.append(actions_list[w-1])
            i -= price[w-1]

        w -= 1

    # Retourner la liste d'éléments sélectionnés
    return selected_elements, count_combinations


def generate_graphs(actions_list: List[Tuple[str, int, float]], max_invest: float) -> None:
    """Fonction pour créer les graphiques"""

    # Charger le fichier CSV pour obtenir la taille de l'entrée
    df = pd.DataFrame(actions_list, columns=['Action', 'Coût (€)', 'Bénéfice (%)'])
    n_values = list(range(1, len(df) + 1))

    # Génération des listes de complexité temporelle et spatiale
    time_complexity = []
    space_complexity = []
    for n in tqdm(n_values, desc="Patientez calcul en cours pour la création des graphiques "):
        actions_subset = df.head(n)
        actions_subset_list = [(row[0], row[1], row[2]) for row in actions_subset.itertuples(index=False)]
        start_time = time.time()
        selected_elements, count_combinations = algorithm_dynamic(actions_subset_list, max_invest, show_progress=False)
        execution_time = time.time() - start_time
        process = psutil.Process()
        memory_used = process.memory_info().rss / 1024 / 1024
        time_complexity.append(execution_time)
        space_complexity.append(memory_used)

    # Création du graphique en deux sous-graphiques
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=False)

    # Sous-graphique 1 : Complexité temporelle
    ax1.plot(
            n_values,
            time_complexity,
            "b.-",
            label="Complexité temporelle\nTemps d'exécution ({:.2f} s)".format(execution_time)
    )

    ax1.scatter(n_values, time_complexity, s=10)
    ax1.set_xlabel("Nombre d\'entrées (n)")
    ax1.set_title("La complexité temporelle de algorithm_dynamic est O(nW)")
    ax1.set_ylabel("Temps (s)")
    ax1.legend()

    # Sous-graphique 2 : Analyse de mémoire
    ax2.set_title("La complexité spatiale de algorithm_dynamic est O(nW)")
    ax2.plot(n_values, space_complexity, "g.-", label="Analyse de mémoire")
    ax2.scatter(n_values, space_complexity, s=10)
    ax2.set_xlabel("Nombre d\'entrées (n)")
    ax2.set_ylabel("Mémoire utilisée (Mo)")
    ax2.legend()

    plt.tight_layout()
    plt.show()


def measure_memory_usage():
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
    console.print("3. dataset3.csv (20 actions)")
    choice = click.prompt("> ", type=click.Choice(["1", "2", "3"]))

    filenames = {
        "1": "dataset1.csv",
        "2": "dataset2.csv",
        "3": "dataset3.csv",
    }
    filename = filenames[choice]

    max_invest_input = click.prompt(
        "Entrez le montant maximal à investir (500€ par défaut)",
        default=500,
        type=float,
    )

    # Lecture du fichier CSV
    actions_list = read_csv(filename)

    # Vérifier si la liste d'actions est vide
    if not actions_list:
        return

    # Mesure du temps d'exécution
    start_time = time.time()

    initial_memory = measure_memory_usage()
    initial_memory_mb = initial_memory / (1024 * 1024)

    # Appel de la fonction algorithm_dynamic avec la liste d'actions et le budget maximal
    selected_elements, count_combinations = algorithm_dynamic(
        actions_list, max_invest_input, show_progress=True
    )

    final_memory = measure_memory_usage()
    final_memory_mb = final_memory / (1024 * 1024)

    # Afficher les résultats
    console.print(
        f"\nActions les plus rentables ({len(selected_elements)} actions) :\n"
    )

    table = Table(title="Résultats")
    table.add_column("Action", style="cyan")
    table.add_column("Coût (€)", style="magenta")
    table.add_column("Bénéfice (%)", style="green")

    for action in selected_elements:
        table.add_row(
            action[0], '{:.2f}'.format(action[1] / 100), '{:.2f}'.format(action[2])
        )

    console.print(table)

    price_total = [action[1] / 100 for action in selected_elements]
    profit_total = [action[2] for action in selected_elements]

    console.print(f"Extraction du fichier {filename}\n", style="bold blue")
    console.print(f"Coût total de l'investissement : {sum(price_total)} €")
    console.print(f"Bénéfice total sur 2 ans : {sum(profit_total):.2f} €")
    console.print(
        f"Bénéfice total sur 2 ans en pourcentage : {((sum(profit_total)/sum(price_total))*100):.2f}%"
    )
    console.print(f"Temps d'exécution : {time.time() - start_time:.2f} secondes")

    # Utiliser intword pour afficher le nombre de combinaisons calculées
    # Avec l'unité de mesure "millions" ou "milliards"
    console.print(
        f"Nombre de combinaisons calculées : {humanize.intword(count_combinations)}(s)\n"
    )

    # Mesure de l'utilisation de la RAM
    console.print(f"Utilisation initiale de la mémoire : {initial_memory_mb:.2f} Mo")
    console.print(f"Utilisation finale de la mémoire : {final_memory_mb:.2f} Mo\n")

    # Demande à l'utilisateur s'il souhaite créer un graphique
    create_graph = click.confirm(
        "Souhaitez-vous créer un graphique à partir des résultats ?", default=False
    )

    if create_graph:
        # Création des graphiques
        generate_graphs(actions_list, max_invest_input)
    else:
        exit()


if __name__ == "__main__":
    main()
