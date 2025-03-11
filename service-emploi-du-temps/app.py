from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, EmploiDuTemps
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:passer@localhost:5432/dbemploi"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

# Ajouter un emploi du temps
@app.route('/emplois', methods=['POST'])
def add_emploi():
    data = request.json
    required_fields = ['date', 'heure', 'cours_id', 'professeur_matricule', 'classe_id']
    
    # Vérifier que tous les champs requis sont présents
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Le champ '{field}' est requis."}), 400

    try:
        # Parser la date et l'heure séparément
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        heure = datetime.strptime(data['heure'], '%H:%M').time()  # Format HH:MM (ex: "14:00")
        emploi = EmploiDuTemps(
            date=date,
            heure=heure,
            cours_id=data['cours_id'],
            professeur_matricule=data['professeur_matricule'],
            classe_id=data['classe_id']
        )
        db.session.add(emploi)
        db.session.commit()
        return jsonify(emploi.to_dict()), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": f"Format de date ou heure invalide: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur lors de l'ajout de l'emploi: {str(e)}"}), 500

# Lister tous les emplois du temps
@app.route('/emplois', methods=['GET'])
def get_emplois():
    try:
        emplois = EmploiDuTemps.query.all()
        return jsonify([e.to_dict() for e in emplois]), 200
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération des emplois: {str(e)}"}), 500

# Obtenir un emploi du temps spécifique
@app.route('/emplois/<int:id>', methods=['GET'])
def get_emploi_by_id(id):
    try:
        emploi = EmploiDuTemps.query.get_or_404(id)
        return jsonify(emploi.to_dict()), 200
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération de l'emploi: {str(e)}"}), 500

# Modifier un emploi du temps
#'%Y-%m-%d'
@app.route('/emplois/<int:id>', methods=['PUT'])
def update_emploi(id):
    try:
        emploi = EmploiDuTemps.query.get_or_404(id)
        data = request.json
        if 'date' in data:
            emploi.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        if 'heure' in data:
            emploi.heure = datetime.strptime(data['heure'], '%H:%M').time()  # Format HH:MM (ex: "14:00")
        emploi.cours_id = data.get('cours_id', emploi.cours_id)
        emploi.professeur_matricule = data.get('professeur_matricule', emploi.professeur_matricule)
        emploi.classe_id = data.get('classe_id', emploi.classe_id)
        db.session.commit()
        return jsonify(emploi.to_dict()), 200
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": f"Format de date ou heure invalide: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur lors de la mise à jour de l'emploi: {str(e)}"}), 500

# Supprimer un emploi du temps
@app.route('/emplois/<int:id>', methods=['DELETE'])
def delete_emploi(id):
    try:
        emploi = EmploiDuTemps.query.get_or_404(id)
        db.session.delete(emploi)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur lors de la suppression de l'emploi: {str(e)}"}), 500

if __name__ == '__main__':
    print("Démarrage du serveur Flask pour service-emploi-du-temps...")
    app.run(port=5005, debug=True)