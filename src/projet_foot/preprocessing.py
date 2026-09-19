import pandas as pd


from projet_foot.utils import add_recent_form
from datetime import datetime

def process_date(df, after, before):
    """A partir des lignes de matchs, formatage des données et suppression des données non intéressantes
    Arguments:
    df --  Dataframe comportant une ligne par match
    after -- on sélectionne uniquement les matchs pami les plus récents

    Returns:
    df -- Dataframe comportant une ligne par match, matchs postérieurs à 'after', triés par ordre croissant de date 
    """
    #Formatage de la date
    df["date"] = pd.to_datetime(df["date"])

    #ajout d'une colonne "year" pour l'année du match
    df["year"] = df["date"].dt.year

    #sélection des matchs postérieurs à 'after' et antérieurs à 'before' (le fichier des matchs est mis à jour quotidiennement)
    df = df[(df["date"] >= after) & (df["date"] < before)]  

    #le dataframe est trié par date croissante et les index sont réinitialisés, et l'index d'origine est supprimé
    return df.sort_values("date").reset_index(drop=True)  #We can use the drop parameter to avoid the old index being added as a column



def process_recent_form(df, window, min_matches):
    """A partir des lignes de matchs, Ajout des données 'form' de chaque équipe pour les matchs précédents
    on ajoute ces informations dans 6 nouvelles colonnes du dataframe (3 pour chaque équipe).
    Arguments:
    df --  Dataframe comportant une ligne par match
    window -- nombre max de matches stockés dans history pour calculer la forme de l'équipe
    min_matches -- nombre min de matches permettant de calculer la forme de l'équipe

    Returns:
    df -- df d'origine augmené des 6 colonnes relatives aux moyennes + 3 liées à leurs différentiels
    """
    df = add_recent_form(df, window, min_matches)
    #suppression de toutes les lignes où au moins une des colonnes indiquées contient un NaN
    df = df.dropna(subset=["home_avg_points", "away_avg_points"]).reset_index(drop=True)
    #Ce qui fait pencher un match, ce n'est pas la forme absolue d'une équipe, c'est l'écart de forme entre les deux adversaires
    # calcul de la différence de forme entre les 2 adversaires, pour nos 3 nouvelles valeurs 
    df['diff_avg_points'] = df['home_avg_points'] - df['away_avg_points']  #on crée une nouvelle colonne "diff_avg_points" qui vaut la différence entre les points moyens de l'équipe à domicile et ceux de l'équipe à l'extérieur
    df['diff_avg_goals_scored'] = df['home_avg_goals_scored'] - df['away_avg_goals_scored']  #on crée une nouvelle colonne "diff_avg
    df['diff_avg_goals_conceded'] = df['home_avg_goals_conceded'] - df['away_avg_goals_conceded']  #on crée une nouvelle colonne "diff_avg_goals_conceded" qui vaut la différence entre les buts encaissés moyens de l'équipe à domicile et ceux de l'équipe à l'extérieur
    return df


def process_match_not_nul(df):
    """ En match de coupe du monde il n'y a pas de match nul, on va donc les écarter  
    Arguments:
    df --  Dataframe comportant une ligne par match

    Returns
    data -- df pour lequel on a supprimé tous les matchs nuls et ajouté une colonne home_win à 1 si match gagné par l'équipe à domicile 0 sinon
    """
    data = df.copy()  #on crée une copie du dataframe df pour ne pas modifier l'original
    data = data[data["home_score"] != data["away_score"]]  #on filtre pour ne garder que les matchs avec un vainqueur (pas de match nul)
    data['home_win'] = (data['home_score'] > data['away_score']).astype(int)  #on crée une nouvelle colonne "home_win" qui vaut 1 si l'équipe à domicile a gagné, 0 sinon
    #print(f"{len(data)} matchs avec un vainqueur")
    return data


def encodage_data(data):
    """ les modèles de machine learning ne travaillant que sur des données numériques, les colonnes neutral et friendly ne sont 
    pas utilisables en l'état pour être utilisées, on va donc les convertir en numérique grâce à l'ajout de 2 colonnes supplémentaires 
    Arguments:
    data --  Dataframe comportant une ligne par match non nul

    Returns
    data -- data augmenté de 2 colonnes numériques
    """
    data["is_neutral"] = data["neutral"].astype(int)  #on crée une nouvelle colonne "is_neutral" qui vaut 1 si le match a lieu sur terrain neutre, 0 sinon
    data["is_friendly"] = (data["tournament"] == "Friendly").astype(int)  #on crée une nouvelle colonne "is_friendly" qui vaut 1 si le match
    return data




def preprocessing_data(df, after="1994-01-01", before=datetime.today(), window = 10, min_matches = 5):
    df_copy = df.copy()  #on crée une copie du dataframe df pour ne pas modifier l'original
    df_copy = process_date(df_copy, after, before)
    df_copy = process_recent_form(df_copy, window, min_matches)
    data = process_match_not_nul(df_copy)
    data = encodage_data(data)
    return data, df
