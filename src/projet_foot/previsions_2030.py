# Simuler toute La Coupe du Monde 2030, match après match
# Avec ce modele, nous pouvons également nous amuser à simuler l'évolution possible de tout un tournoi !
# Pour l'illustrer, je propose qu'on se penche sur la CDM de 2030.
# Celle-ci se jouera en Espagne, au Portugal et au Maroc, avec un format à 48 équipes. 
# Pour rester simples, on imagine une phase finale à l'ancienne : **32 équipes plausibles, un tableau à élimination directe, 
# des seizièmes de finale jusqu'à la finale**. Autres simplifications assumées : tous les matchs sur terrain neutre, 
# aucun match amical, et pas de match nul possible (le modèle tranche toujours, comme les tirs au but).


from projet_foot.machine_learning import predict_match


FLAGS = {
    "Spain": "🇪🇸", "Portugal": "🇵🇹", "Morocco": "🇲🇦", "France": "🇫🇷",
    "Brazil": "🇧🇷", "Argentina": "🇦🇷", "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Germany": "🇩🇪",
    "Netherlands": "🇳🇱", "Belgium": "🇧🇪", "Croatia": "🇭🇷", "Italy": "🇮🇹",
    "Uruguay": "🇺🇾", "Colombia": "🇨🇴", "Japan": "🇯🇵", "United States": "🇺🇸",
    "Mexico": "🇲🇽", "Senegal": "🇸🇳", "Switzerland": "🇨🇭", "Denmark": "🇩🇰",
    "South Korea": "🇰🇷", "Australia": "🇦🇺", "Canada": "🇨🇦", "Ghana": "🇬🇭",
    "Poland": "🇵🇱", "Austria": "🇦🇹", "Turkey": "🇹🇷", "Ecuador": "🇪🇨",
    "Nigeria": "🇳🇬", "Serbia": "🇷🇸", "Greece": "🇬🇷", "Egypt": "🇪🇬",
}

ROUND_NAMES = [
    "Seizièmes de finale",
    "Huitièmes de finale",
    "Quarts de finale",
    "Demi-finales",
    "Finale",
]

round_of_32 = [
    ("Spain", "Greece"), ("Denmark", "Ecuador"),
    ("Argentina", "Egypt"), ("Netherlands", "Poland"),
    ("France", "Nigeria"), ("Croatia", "South Korea"),
    ("England", "Canada"), ("Italy", "Senegal"),
    ("Portugal", "Australia"), ("Belgium", "Turkey"),
    ("Brazil", "Ghana"), ("Uruguay", "Switzerland"),
    ("Morocco", "Serbia"), ("Mexico", "Austria"),
    ("Germany", "Colombia"), ("Japan", "United States"),
]

def team_label(team):
    """Retourne le nom de l'équipe avec son flag."""
    return f"{FLAGS.get(team, '🏳️')} {team}"


def print_round(round_name, match_results):
    """affichage des résultats du round round-name.

    Arguments:
    round_name -- nom du round, ex 'Quarts de finale'
    match_results -- liste de tuples (team_a, team_b, winner, win_probability)
    """
    print(f"\n{'=' * 60}")
    print(f"  {round_name.upper()}")
    print("=" * 60)
    for team_a, team_b, winner, probability in match_results:
        line = f"{team_label(team_a):<22} vs {team_label(team_b):<22}"
        print(f"{line} -> {team_label(winner)} ({probability:.0%})")


def print_champion(team):
    """affichage du gagnant."""
    print(f"\n{'*' * 60}")
    print(f"   🏆 CHAMPION DU MONDE 2030 : {team_label(team).upper()} 🏆")
    print("*" * 60)


def simulate_world_cup_2030(scaler, model, df):
    current_round = round_of_32
    all_results = []

    for round_name in ROUND_NAMES:
        results = []
        winners = []

        for team_a, team_b in current_round:

            ### START CODE HERE ###
            winner, probability = predict_match(team_a, team_b, scaler, model, df)
            winners.append(winner)
            results.append((team_a, team_b, winner, float(probability)))
            ### END CODE HERE ###

        print_round(round_name, results)
        all_results.extend(results)
        current_round = list(zip(winners[::2], winners[1::2]))

    champion = winners[0]
    print_champion(champion)
    return champion, all_results


