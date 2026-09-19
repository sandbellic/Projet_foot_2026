from collections import defaultdict, deque

import pandas as pd

DATA_URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"


def load_matches(base_dir):
    """Charge les résultats internationaux des matches dans un dataframe
    enregistre une copie dans fichier .csv
    Arguments:
    base_dir -- répertoire de base où enregistrer le fichier results.csv

    Returns:
    df -- Dataframe comportant une ligne par match, 
    """
    # Chargement des données .csv directement à partir de l'URL site github (DATA_URL)
    df = pd.read_csv(DATA_URL)
    # copie locale du fichier .csv dans le répertoire data du projet
    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)  # création du répertoire data
    path = data_dir / "results.csv"
    df.to_csv(path, index=False)
    return df


def _points(goals_for, goals_against):   #fonction privée (préfixée par un underscore) qui calcule le nombre de points obtenus pour un match donné en fonction des buts marqués et encaissés
    """Retourne le nb de points gagnés par match (3/1/0)."""
    if goals_for > goals_against:
        return 3
    if goals_for == goals_against:
        return 1
    return 0


def add_recent_form(df, window=10, min_matches=5):
    """
    Pour chaque match on va regarder quelle était la forme de chaque équipe avant d'effectuer le match,
    ie on va regarder les `window` derniers matchs de chaque équipe avant le match en question, 
    et calculer la moyenne des points (3, 1 ou 0), des buts marqués et des buts encaissés sur ces matchs.
    on ne prend en compte que les 'window' matchs joués AVANT le match en question, et non le match lui-même.
    on le fait pour les deux équipes (home et away) de chaque match, 
    et on ajoute ces informations dans 6 nouvelles colonnes du dataframe (3 pour chaque équipe).
    la forme de chaque équipe est stockée dans un dictionnaire (history) avec comme clé le nom de l'équipe
    et comme valeur les `window` derniers matchs de chaque équipe avant le match en question
    Il faut qu'une équipe ait joué au moins `min_matches` pour que les 3 moyennes soient calculées, sinon
    les valeurs sont mises à NaN.

    Arguments:
    df -- DataFrame reprenant les matches, trié par date
    window -- nombre max de matches stockés dans history pour calculer la forme de l'équipe
    min_matches -- nombre min de matches permettant de calculer la forme de l'équipe

    Returns:
    df -- df d'origine augmené des 6 colonnes relatives aux moyennes :
          home_avg_points, home_avg_goals_scored, home_avg_goals_conceded,
          away_avg_points, away_avg_goals_scored, away_avg_goals_conceded
    """ 
    history = defaultdict(lambda: deque(maxlen=window))    # pour enregistrer l'historique des 'window' derniers matchs de chaque équipe 
                                                           # quand on va enregistrer un nouveau match, le plus ancien sera automatiquement 
                                                           # supprimé de la liste si on en a plus de 'window' matchs
    new_columns = []   # liste pour stocker les 6 nouvelles colonnes à ajouter au dataframe

    for row in df.itertuples():  # on boucle sur chaque match du dataframe, on forme un tuple à partir de chaque ligne du dataframe, ce qui permet d'accéder aux colonnes par leur nom (ex: row.home_team)
        features = {}       #dictionnaire pour stocker les 6 nouvelles colonnes pour le match en cours
        for side, team in [("home", row.home_team), ("away", row.away_team)]:    #on passe 2 fois dans la boucle, une fois pour l'équipe à domicile et une fois pour l'équipe à l'extérieur
            past = history[team]            #on récupère l'historique des 'window' derniers matchs de l'équipe
            if len(past) >= min_matches:    #on ne calcule les moyennes que si l'équipe a joué au moins 'min_matches' matchs
                features[f"{side}_avg_points"] = sum(m[0] for m in past) / len(past)
                features[f"{side}_avg_goals_scored"] = sum(m[1] for m in past) / len(past)
                features[f"{side}_avg_goals_conceded"] = sum(m[2] for m in past) / len(past)
        new_columns.append(features)        #on sauvegarde le dictionnaire des 6 statistiques du match en cours dans la liste new_columns
                                            #chaque élément de liste est de la forme {"home_avg_points": 2.0, "home_avg_goals_scored": 1.5, "home_avg_goals_conceded": 0.5, "away_avg_points": 1.0, "away_avg_goals_scored": 1.0, "away_avg_goals_conceded": 1.0}
        for team, goals_for, goals_against in [
            (row.home_team, row.home_score, row.away_score),
            (row.away_team, row.away_score, row.home_score),
        ]:
            history[team].append((_points(goals_for, goals_against), goals_for, goals_against))  #on met à jour l'historique de l'équipe avec les stats du match en cours (points, buts marqués, buts encaissés)
                                        # en ne gardant que les 'window' derniers matchs grâce au deque avec maxlen=window
    form_df = pd.DataFrame(new_columns, index=df.index)   #on transforme la liste de dictionnaires new_columns en un dataframe, avec les mêmes index que le dataframe d'origine
    return pd.concat([df, form_df], axis=1)     #ainsi on peut concaténer le dataframe d'origine avec le dataframe des nouvelles colonnes, en gardant les mêmes index, et on retourne le nouveau dataframe
#pour chaque match, on a maintenant les 6 nouvelles colonnes avec les moyennes des 'window' derniers matchs de chaque équipe avant le match en question
#au début comme l'histrique est vide, les premières lignes du dataframe auront des valeurs NaN pour ces colonnes, car il n'y a pas assez de matchs passés pour calculer les moyennes


def get_current_form(df, team, window=10):
    """
    Récupère les statistiques sur les 'window' derniers matchs de l'équipe 'team' dans le dataframe df, 
    et calcule la moyenne des points, buts marqués et buts encaissés sur ces matchs.
    
    Arguments:
    df -- DataFrame reprenant les matches, trié par date
    team -- Nom de l'équipe
    window -- nombre max de matches qui a servi à calculer la forme de l'équipe,  les 
              ie les matches précédents celui en cours

    Returns:
    form -- dict with keys 'avg_points', 'avg_goals_scored', 'avg_goals_conceded'
    """
    mask = (df["home_team"] == team) | (df["away_team"] == team)    #on récupère uniquement les matches de l'équipe 'team', que ce soit à domicile ou à l'extérieur
    last_matches = df[mask].tail(window)   #on récupère les 'window' derniers matchs de l'équipe 'team', en utilisant la méthode tail() qui retourne les dernières lignes du dataframe
    if last_matches.empty:
        raise ValueError(f"Aucun match trouvé pour l'équipe '{team}'. Vérifie l'orthographe (noms en anglais).")

    points, scored, conceded = [], [], []
    for row in last_matches.itertuples():    #sur les 'window' derniers matchs de l'équipe, on calcule les points, buts marqués et buts encaissés pour chaque match
        if row.home_team == team:
            goals_for, goals_against = row.home_score, row.away_score   #récupération des buts marqués et encaissés à domicile
        else:
            goals_for, goals_against = row.away_score, row.home_score  #récupération des buts marqués et encaissés à l'extérieur
        points.append(_points(goals_for, goals_against))
        scored.append(goals_for)
        conceded.append(goals_against)

    n = len(points)
    return {
        "avg_points": sum(points) / n,
        "avg_goals_scored": sum(scored) / n,
        "avg_goals_conceded": sum(conceded) / n,
    }

