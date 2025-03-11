from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Classe

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:passer@localhost:5432/dbclasse"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()


# Ajouter une classe

@app.route('/classes', methods = ['POST'])
def add_classe():
    data = request.json
    classe = Classe(
        id = data['id'],
        nom = data['nom'],
        description = data.get('description', ''),
        niveau = data.get('niveau','')
    )
    db.session.add(classe)
    db.session.commit()
    return jsonify(classe.to_dict()), 201


#Afficher tous les classes

@app.route('/classes', methods = ['GET'])
def get_classes():
    classes = Classe.query.all()
    return jsonify([classe.to_dict() for classe in classes])


# Obtenir une classe spécifique 
@app.route('/classes/<string:id>', methods = ['GET'])
def get_classe(id):
    classe = Classe.query.get_or_404(id)
    return jsonify(classe.to_dict())

# Modifier une classe
@app.route('/classes/<string:id>', methods = ['PUT'])
def update_classe(id):
    classe = Classe.query.get_or_404(id)
    data =  request.json
    classe.nom = data.get('nom', classe.nom)
    classe.description = data.get('description', classe.description)
    classe.niveau = data.get('niveau', classe.niveau)
    db.session.commit()
    return jsonify(classe.to_dict())


# Supprimer une classe 
@app.route('/classes/<string:id>', methods = ['DELETE'])
def delete_classe(id):
    classe = Classe.query.get_or_404(id)
    db.session.delete(classe)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    print("Démarrage du serveur Flask pour service-classes...")
    app.run(port=5002, debug=True)