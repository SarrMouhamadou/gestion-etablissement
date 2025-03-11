from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Cours
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:passer@localhost:5432/dbcours"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

# Ajouter un cours
@app.route('/cours', methods=['POST'])
def add_cours():
    data = request.json
    required_fields = ['nom']  # Seul 'nom' est requis
    
    # Vérifier que les champs requis sont présents
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Le champ '{field}' est requis."}), 400

    # Vérifier le professeur si fourni (optionnel)
    professeur_matricule = data.get('professeur_matricule')
    if professeur_matricule:
        prof_url = f"http://127.0.0.1:5003/professeurs/{professeur_matricule}"
        try:
            response = requests.get(prof_url)
            if response.status_code != 200:
                return jsonify({"error": f"Le professeur avec matricule {professeur_matricule} n'existe pas."}), 404
        except requests.RequestException:
            return jsonify({"error": "Impossible de vérifier le professeur (service-profs inaccessible)."}), 500

    try:
        cours = Cours(
            nom=data['nom'],  # Changement de 'titre' à 'nom'
            description=data.get('description', ''),  # Optionnel, défaut vide
            professeur_matricule=professeur_matricule  # Optionnel, None si non fourni
        )
        db.session.add(cours)
        db.session.commit()
        return jsonify(cours.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur lors de l'ajout du cours: {str(e)}"}), 500

# Lister tous les cours
@app.route('/cours', methods=['GET'])
def get_cours():
    try:
        cours = Cours.query.all()
        return jsonify([c.to_dict() for c in cours]), 200
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération des cours: {str(e)}"}), 500

# Obtenir un cours spécifique
@app.route('/cours/<int:id>', methods=['GET'])
def get_cours_by_id(id):
    try:
        cours = Cours.query.get_or_404(id)
        return jsonify(cours.to_dict()), 200
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération du cours: {str(e)}"}), 500

# Modifier un cours
@app.route('/cours/<int:id>', methods=['PUT'])
def update_cours(id):
    try:
        cours = Cours.query.get_or_404(id)
        data = request.json
        cours.nom = data.get('nom', cours.nom)  # Changement de 'titre' à 'nom'
        cours.description = data.get('description', cours.description)
        professeur_matricule = data.get('professeur_matricule', cours.professeur_matricule)
        if professeur_matricule != cours.professeur_matricule and professeur_matricule is not None:
            prof_url = f"http://127.0.0.1:5003/professeurs/{professeur_matricule}"
            response = requests.get(prof_url)
            if response.status_code != 200:
                return jsonify({"error": f"Le professeur avec matricule {professeur_matricule} n'existe pas."}), 404
        cours.professeur_matricule = professeur_matricule
        db.session.commit()
        return jsonify(cours.to_dict()), 200
    except requests.RequestException:
        return jsonify({"error": "Impossible de vérifier le professeur (service-profs inaccessible)."}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur lors de la mise à jour du cours: {str(e)}"}), 500

# Supprimer un cours
@app.route('/cours/<int:id>', methods=['DELETE'])
def delete_cours(id):
    try:
        cours = Cours.query.get_or_404(id)
        db.session.delete(cours)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur lors de la suppression du cours: {str(e)}"}), 500

if __name__ == '__main__':
    print("Démarrage du serveur Flask pour service-cours...")
    app.run(port=5004, debug=True)