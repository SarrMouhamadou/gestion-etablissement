from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Cours(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), nullable=False)  # Changement de 'titre' à 'nom'
    description = db.Column(db.String(200), nullable=True)  # Nullable pour rendre optionnel
    professeur_matricule = db.Column(db.String(20), nullable=True)  # Rendu optionnel, pas de ForeignKey

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'description': self.description,
            'professeur_matricule': self.professeur_matricule
        }