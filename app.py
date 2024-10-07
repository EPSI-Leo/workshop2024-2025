from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

# Initialisation de l'application Flask
app = Flask(__name__)

# Clé API pour CalorieNinjas
API_KEY = os.getenv("API_KEY")
API_URL = "https://api.calorieninjas.com/v1/nutrition?query="

# Fonction pour interroger l'API CalorieNinjas et obtenir les informations nutritionnelles
def get_nutrition_info(query):
    headers = {'X-Api-Key': API_KEY}
    response = requests.get(API_URL + query, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Page d'accueil
@app.route('/')
def index():
    return render_template("index.html")

# Route pour calculer la dose d'insuline
@app.route('/calculer', methods=['POST'])
def calculer():
    poids = float(request.form['poids'])
    glycémie_actuelle = float(request.form['glycemie_actuelle'])
    glycémie_cible = float(request.form['glycemie_cible'])
    facteur_sensibilité = float(request.form['facteur_sensibilite'])

    # Vérification si le facteur de sensibilité est égal à 0
    if facteur_sensibilité == 0:
        erreur_sensibilite = "Le facteur de sensibilité ne peut pas être égal à 0. Veuillez entrer une valeur valide."
        return render_template("index.html", erreur_sensibilite=erreur_sensibilite)

    # Calcul du Total Daily Dose (TDD) et ratio insuline/glucides
    tdd = 0.55 * poids
    ratio_insuline_glucides = 500 / tdd

    # Récupération des aliments et quantités saisis par l'utilisateur
    aliments = request.form.getlist('aliments')
    quantites = request.form.getlist('quantites')
    glucides_total = 0.0
    erreurs = []  # Liste pour enregistrer les erreurs
    aliments_inconnus = []  # Liste des aliments introuvables

    # Calcul du total de glucides en utilisant CalorieNinjas
    for aliment, quantite in zip(aliments, quantites):
        query = f"{quantite}g {aliment}"
        data = get_nutrition_info(query)
        if data and 'items' in data and len(data['items']) > 0:
            glucides = data['items'][0]['carbohydrates_total_g']  # Récupérer les glucides
            glucides_total += glucides
        else:
            # Ajouter un message d'erreur si l'aliment n'est pas trouvé
            erreurs.append(f"L'aliment '{aliment}' n'a pas été trouvé dans la base de données.")
            aliments_inconnus.append(aliment)

    # Calcul de la dose d'insuline si tous les aliments ont été trouvés
    if not erreurs:
        dose_glucides = glucides_total / ratio_insuline_glucides
        correction_glycémie = (glycémie_actuelle - glycémie_cible) / facteur_sensibilité
        dose_totale = round(dose_glucides + correction_glycémie, 2)
        return render_template("index.html", dose=dose_totale, ratio=round(ratio_insuline_glucides, 2), glucides_total=glucides_total)
    else:
        # Si des erreurs existent, les afficher sur le front-end
        return render_template("index.html", erreurs=erreurs, aliments_inconnus=aliments_inconnus)

# Exécution de l'application
if __name__ == "__main__":
    app.run(debug=True)
