from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Classe(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    description =  db.Column(db.String(200), nullable=False)
    niveau = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'description': self.description,
            'niveau': self.niveau
        }