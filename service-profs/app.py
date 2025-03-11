from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Professeur

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:passer@localhost:5432/dbprofs"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()


# Ajouter un professeur
@app.route('/professeurs', methods = ['POST'])
def add_professeur():
    data = request.json
    professeur = Professeur(
        matricule=data['matricule'],
        nom = data['nom'],
        prenom = data['prenom'],
        email = data['email'],
        matiere = data['matiere']
    )
    db.session.add(professeur)
    db.session.commit()
    return jsonify(professeur.to_dict()), 201

# Lister tous les professeurs
@app.route('/professeurs', methods=['GET'])
def get_professeurs():
    professeurs = Professeur.query.all()
    return jsonify([professeur.to_dict() for professeur in professeurs])


# Obtenir un professeur spécifique
@app.route('/professeurs/<string:matricule>', methods=['GET'])
def get_professeur(matricule):
    professeur = Professeur.query.get_or_404(matricule)
    return jsonify(professeur.to_dict())

# Modifier un professeur
@app.route('/professeurs/<string:matricule>', methods=['PUT'])
def update_professeur(matricule):
    professeur = Professeur.query.get_or_404(matricule)
    data = request.json
    professeur.nom = data.get('nom', professeur.nom)
    professeur.prenom = data.get('prenom', professeur.prenom)
    professeur.email = data.get('email', professeur.email)
    professeur.matiere = data.get('matiere', professeur.matiere)
    db.session.commit()
    return jsonify(professeur.to_dict())

# Supprimer un professeur

@app.route('/professeurs/<string:matricule>', methods = ['DELETE'])
def delete_professeur(matricule):
    professeur = Professeur.query.get_or_404(matricule)
    db.session.delete(professeur)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    print("Démarrage du serveur Flask pour service-profs...")
    app.run(port=5003, debug=True)

