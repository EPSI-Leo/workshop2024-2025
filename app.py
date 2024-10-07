from flask import Flask, render_template, request

# Initialisation de l'application Flask
app = Flask(__name__)

# Base de données simple pour les aliments avec leur teneur en glucides (en grammes pour 100g)
base_aliments = {
    "pomme": 12.0,  # 12g de glucides pour 100g de pomme
    "riz": 28.0,  # 28g de glucides pour 100g de riz
    "poulet": 0.0,  # 0g de glucides pour 100g de poulet
    "pain": 50.0,  # 50g de glucides pour 100g de pain
    "banane": 22.0  # 22g de glucides pour 100g de banane
}

# Page d'accueil avec formulaire
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

    # Calcul du Total Daily Dose (TDD) et ratio insuline/glucides
    tdd = 0.55 * poids
    ratio_insuline_glucides = 500 / tdd

    # Calcul du total de glucides en fonction des aliments sélectionnés
    aliments = request.form.getlist('aliments')
    quantites = request.form.getlist('quantites')
    glucides_total = 0.0
    for aliment, quantite in zip(aliments, quantites):
        if aliment in base_aliments:
            glucides = (base_aliments[aliment] / 100) * float(quantite)
            glucides_total += glucides

    # Calcul de la dose d'insuline nécessaire
    dose_glucides = glucides_total / ratio_insuline_glucides
    correction_glycémie = (glycémie_actuelle - glycémie_cible) / facteur_sensibilité
    dose_totale = round(dose_glucides + correction_glycémie, 2)

    return render_template("index.html", dose=dose_totale, ratio=round(ratio_insuline_glucides, 2), glucides_total=glucides_total)

# Exécution de l'application
if __name__ == "__main__":
    app.run(debug=True)
