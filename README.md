Projet_foot_2026 est réalisé à partir des mini-projets Data / IA proposés par le site ** Machine Learnia Ltd ** durant l'été 2026.

Guillaume Saint-Cirgue, Fondateur du site et Senior Data Scientist avec plus de 10 ans d’expérience dans les secteurs de la tech, l’aviation, la robotique, l’énergie, et les usines connectées nous fait partager ses connaissances dans le domaine de l’intelligence artificielle.

Au travers de projets partagés, guidés étape par étape, avec des explications claires, il aborde des sujets relatifs :
 * au Machine Learning - Projet football, coupe du monde 

J'ai réalisé ce projet et ai décidé de le modifier librement en ajoutant mes propres commentaires et codes.

Environnement : 
1 . Utilisation de uv comme outil de gestion de l'environnement de Python : pour créer facilement un environnement virtuel,
décrire le projet et gérer mes dépendances via le fichier pyproject.toml 
2 . Présence d'un folder dist contenant une version exécutable du projet (simple .exe ou possibilité d'avoir un setup), pas de représentation graphique.


********************************************

L'objectif ici est de construire un modèle de Machine Learning capable de prédire le vainqueur d'un match de football, à l'international. Ici vainqueur du mondial 2026.

La prédiction va s'appuyer sur les données disponibles passées.
On dispose d'un jeu de données librement réutilisable (licence CC0, domaine public) qui recense TOUS les matchs internationaux de 
football depuis 1872. Plus de 49 000 matchs : Coupes du Monde, championnats continentaux, qualifications, matchs amicaux...
Les données d'origine sont disponibles ici https://github.com/martj42/international_results, et maintenues à jour.

On va passer par les étapes suivantes :
1. Récupération des données : chargement du jeu de données, exploration et visualisation
2. Prétraitement des données : nettoyage, transformation, création de nouvelles features, choix des features pertinentes pour la modélisation
3. Modélisation : entraînement d'un modèle de Machine Learning sur les données prétraitées
4. Prédiction : utilisation du modèle entraîné pour prédire le vainqueur d'un match donné


1. Récupération des données 
   
   Chargement du fichier csv présent à l'URL : "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
   Sa structure initiale : 
   | Colonne | Description |
    |---|---|
    | `date` | la date du match |
    | `home_team` | l'équipe qui reçoit |
    | `away_team` | l'équipe qui se déplace |
    | `home_score` | buts de l'équipe à domicile |
    | `away_score` | buts de l'équipe à l'extérieur |
    | `tournament` | le type de compétition (Coupe du Monde, amical...) |
    | `city`, `country` | où le match a été joué |
    | `neutral` | `True` si le match s'est joué sur terrain neutre |
    
    on va charger les données dans un dataframe, et conserver le fichier dans notre répertoire data sous projet_foot.

2. Prétraitement des données
Notre objectif est de déterminer quel va être le vainqueur de la finale du mondial 2026.
   * On a tous les matchs internationaux depuis 1872. On filtre pour conserver uniquement un historique de 30 ans (matchs postérieurs à 01/01/1994 et antérieur strict au 19/07/2026 jour de la finale) => environ 30 000 matchs 
   * Les nombres de buts à domicile / extérieur, ... ne sont pas des features suffisantes pour le notre objectif. Le vainqueur sera l'équipe la plus forte à un instant donné. Mais comment déterminer la force d'une équipe à un instant donné ? Une idée simple et efficace : regarder ses résultats sur les 10 matchs précédents. Une équipe qui a pris beaucoup de points et marqué beaucoup de buts récemment est en forme. Pour tous les matchs on va donc calculer cette récente forme (moyenne) => cf dans utils la fonction add_recent_form. On va obtenir 6 nouvelles colonnes (3 pour home : `home_avg_points`, `home_avg_goals_scored`, `home_avg_goals_conceded`, 3 pour away)
   * Pour les matchs les plus anciens, la forme de l'équipe n'a pas pu être calculée. On a donc des valeurs nulles dans nos nouvelles colonnes pour ces matchs. On doit les enlever sous peine de voir planter notre modèle de ML => reste environ 20 000 matchs
   * On est sur la prédiction du vainqueur d'un mondial : le nul n'existe pas. On va donc supprimer tous les matchs nuls => reste eviron 15 000 matchs
   * On veut prédire le nom du vainqueur : ie celui de home_team ou away_team qui a le plus grand score. On va donc créer 1 nouvelle colonne home_win qui prendra 1 quand home_score sera supérieur à away_score, 0 si non.
   * Dans nos features on veut garder les colonnes 'tournament' et 'neutral'. Le modèle n'accepte que des données numériques. On doit encoder les valeurs de ces colonnes. On créer donc 2 nouvelles colonnes is_neutral (0/1), is_friendly (0/1)
   * La forme des équipe est intéressante pour nos features. Mais plutôt que de garder nos 6 colonnes telles quelles, on va retenir leur différentiel (on ajoute 3 colonnes)

3. Modélisation : entraînement d'un modèle de Machine Learning sur les données prétraitées
on a nos 5 features => "diff_avg_points", "diff_avg_goals_scored","diff_avg_goals_conceded", "is_neutral", "is_friendly"
et notre cible : "home_win"
  * On découpe avec train_test_split
  * On met les features à l'échelle en les standardisant avec Standardscaler
  * On utilise le modèle RandomForestClassifier (avec 200 arbres) 
  * On l'entraîne sur les données de d'entrainement 
  * On prédit les résultats sur les données de test
  * On vérifie la performance du modèle

4. On utilise le modèle pour prédire le vainqueur de la finale