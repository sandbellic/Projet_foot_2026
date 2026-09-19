
from projet_foot.utils import load_matches
from projet_foot.preprocessing import preprocessing_data 
from projet_foot.machine_learning import ml, predict_match
from pathlib import Path
from projet_foot.previsions_2030 import simulate_world_cup_2030


def main():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    df = load_matches(BASE_DIR)
    data, df = preprocessing_data(df, before="2026-07-19")
    scaler, model = ml(data)


    print(f"\n{'*' * 60} \n\nPrediction du match de finale de la Coupe du Monde 2026 : Spain vs Argentina")
    winner, probability = predict_match("Spain", "Argentina", scaler, model, df)
    print(f" 🏆 CHAMPION DU MONDE 2026 : victoire de {winner} ({probability:.0%})\n\n{'*' * 60}\n\n\n")

    # Prévisions Résultats de la Coupe du Monde 2030
    # on va utiliser les données de matchs jusqu'à aujourd'hui pour prédire les résultats de la coupe du monde 2030, 
    # au fur et à mesure que les matchs de qualification auront lieu, on pourra mettre à jour les données et refaire la prédiction
    data, df = preprocessing_data(df)    # before=datetime.today()
    scaler, model = ml(data)
    print(f"\n{'*' * 60} \n\nPrédiction des Résultats de la Coupe du Monde 2030")
    champion, all_results = simulate_world_cup_2030(scaler, model, df)



if __name__ == "__main__":
    main()