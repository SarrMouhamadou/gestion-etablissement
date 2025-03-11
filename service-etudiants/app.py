from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Etudiant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:passer@localhost:5432/dbetudiant"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

# Script temporaire pour mettre à jour les étudiants existants (exécuter une seule fois, puis commenter ou supprimer)
#with app.app_context():
#    etudiants = Etudiant.query.all()
#    for etudiant in etudiants:
#        if not etudiant.classe_id:  # Si classe_id est None ou vide
#            etudiant.classe_id = 'C1'  # Remplacez 'C1' par un ID de classe valide existant
#    db.session.commit()
#    print("Étudiants mis à jour avec classe_id par défaut.")

# Fonction pour ajouter un étudiant
@app.route('/etudiants', methods=['POST'])
def add_etudiant():
    data = request.json
    etudiant = Etudiant(
        matricule=data['matricule'],
        nom=data['nom'],
        prenom=data['prenom'],
        email=data['email'],
        classe_id=data['classe_id']  # Gestion de classe_id
    )
    db.session.add(etudiant)
    db.session.commit()
    return jsonify(etudiant.to_dict()), 201

# Fonction pour afficher tous les étudiants
@app.route('/etudiants', methods=['GET'])
def get_etudiants():
    etudiants = Etudiant.query.all()
    result = [etudiant.to_dict() for etudiant in etudiants]
    print("Données des étudiants:", result)  # Débogage
    return jsonify(result)

# Fonction pour afficher un étudiant selon son matricule
@app.route('/etudiants/<string:matricule>', methods=['GET'])
def get_etudiant(matricule):
    etudiant = Etudiant.query.get_or_404(matricule)
    return jsonify(etudiant.to_dict())

# Fonction pour modifier un étudiant
@app.route('/etudiants/<string:matricule>', methods=['PUT'])
def update_etudiant(matricule):
    etudiant = Etudiant.query.get_or_404(matricule)
    data = request.json
    etudiant.nom = data.get('nom', etudiant.nom)
    etudiant.prenom = data.get('prenom', etudiant.prenom)
    etudiant.email = data.get('email', etudiant.email)
    etudiant.classe_id = data.get('classe_id', etudiant.classe_id)  # Mise à jour de classe_id
    db.session.commit()
    return jsonify(etudiant.to_dict())

# Fonction pour supprimer un étudiant
@app.route('/etudiants/<string:matricule>', methods=['DELETE'])
def delete_etudiant(matricule):
    etudiant = Etudiant.query.get_or_404(matricule)
    db.session.delete(etudiant)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    print("Démarrage du serveur Flask...")
    app.run(port=5000, debug=True)