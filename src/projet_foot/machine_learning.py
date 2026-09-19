from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import matplotlib.pyplot as plt
import pandas as pd
from projet_foot.utils import get_current_form

FEATURES = [
    "diff_avg_points",
    "diff_avg_goals_scored",
    "diff_avg_goals_conceded",
    "is_neutral",
    "is_friendly",
]

def ml(data):

    """
    Arguments:
    data --  Dataframe préparé grace au preprocessing pour être exploité par le modèle de ML

    Returns
     -- 
    """
 
    #DEFINITION DES FEATURES ET DE LA CIBLE
    X = data[FEATURES]        #on a retenu 5 variables numériques explicatives (différence de points moyens, différence de buts marqués, différence de buts encaissés, match sur terrain neutre, match amical)
    y = data['home_win']      #variable cible (1 si l'équipe à domicile a gagné, 0 sinon)

    #DECOUPAGE DES DONNEES en jeu d'entraînement (80%) et jeu de test (20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42) 

    #STANDARDISATION DES DONNEES
    #il s'agit de mettre mettre toutes les features à la même échelle.
    #Le `StandardScaler` de scikit-learn transforme chaque colonne pour qu'elle soit centrée autour de 0 avec un écart-type de 1.
    #certains modèles sont perturbés quand les feature ont des valeurs d'ordre différent: les plus "grandes" écrasant les autres. 
    #(pas vraiment utile dans le cadre de notre modèle de randomforest qui est peut sensible à des différences d'échelle entre features)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)  #calcule la moyenne et l'écart-type sur le jeu d'entraînement puis transforme les données.
    X_test_scaled = scaler.transform(X_test)        #on applique la même transformation au jeu de test

    #DEFINITION DU MODELE CHOISI et on l'ENTRAINE sur les données de train scalés, 
    #une fois le modèle entrainé, on l'utilise pour faire la prédiction sur les données de test scalés
    #on calcule la performance en comparant les prédictions aux vrais résultats
    model = RandomForestClassifier(n_estimators=200, random_state=42)  #on crée un modèle de forêt aléatoire avec 200 arbres et une graine aléatoire fixe pour la reproductibilité
    model.fit(X_train_scaled, y_train)  #on entraîne le modèle sur les données d'entraînement
    y_pred = model.predict(X_test_scaled)  #on prédit les résultats sur les données de test, on veut voir si le modèle généralise bien
    accuracy = accuracy_score(y_test, y_pred)  #on calcule la performance du modèle, en comparant les prédictions obtenues sur les données de test avec les vraies valeurs
    
    #VERIFICATION DE LA PERTINENCE DU MODELE
    #print(f"Accuracy du modèle : {accuracy:.1%}, à mettre en comparaison avec la moyenne réelle (toujours prédire une victoire à domicile) {y_test.mean()}")
    #ConfusionMatrixDisplay.from_estimator(
    #        model, X_test_scaled, y_test,
    #        display_labels=["Pas de victoire domicile", "Victoire domicile"],
    #        cmap="Blues", colorbar=False,
    #    )
    #plt.title("Matrice de confusion sur le jeu de test")
    #plt.tight_layout()
    #plt.show()

    return scaler, model


def predict_match(team_a, team_b, scaler, model, df):
    """Predict the winner of a match between two teams on neutral ground.

    Arguments:
    team_a -- name of the first team, e.g. 'France'
    team_b -- name of the second team, e.g. 'Brazil'

    Returns:
    winner -- name of the predicted winner
    probability -- probability of the winner winning (between 0.5 and 1)
    """

    ### START CODE HERE ###
    # get_current_form retourne un dictionnaire
    #team_a = 'home', team_b = 'away'
    dict_a = get_current_form(df, team_a)
    dict_b = get_current_form(df, team_b)
    diff_point = dict_a['avg_points'] - dict_b['avg_points']
    diff_goals_scored = dict_a['avg_goals_scored'] - dict_b['avg_goals_scored']
    diff_goals_conced = dict_a['avg_goals_conceded'] - dict_b['avg_goals_conceded']
    is_neutral = 1
    is_friendly = 0

    features = pd.DataFrame([[diff_point, diff_goals_scored, diff_goals_conced, is_neutral, is_friendly]],columns=FEATURES)
    features_scaled = scaler.transform(features)
    y = model.predict(features_scaled)
    #display(model.predict_proba(features_scaled))
    proba = model.predict_proba(features_scaled)
    proba_a_wins = proba[0][1]   #!!!`model.predict_proba(...)` renvoie `[[proba_classe_0, proba_classe_1]]`, la classe 1 étant la victoire de l'équipe "à domicile", ici l'équipe A
    ### END CODE HERE ###

    if proba_a_wins >= 0.5:
        return team_a, proba_a_wins
    return team_b, 1 - proba_a_wins

