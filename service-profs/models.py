from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Professeur(db.Model):
    matricule = db.Column(db.String(20), primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    matiere = db.Column(db.Integer, nullable=False)  # Changement en Integer pour référencer cours.id

    def to_dict(self):
        return {
            'matricule': self.matricule,
            'nom': self.nom,
            'prenom': self.prenom,
            'email': self.email,
            'matiere': self.matiere
        }