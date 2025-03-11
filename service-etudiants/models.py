from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Etudiant(db.Model):
    matricule = db.Column(db.String(20), primary_key=True)
    nom = db.Column(db.String(20), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    classe_id = db.Column(db.String(20), nullable=True)


    def to_dict(self):
        return {
            'matricule': self.matricule,
            'nom': self.nom,
            'prenom': self.prenom,
            'email': self.email,
            'classe_id': self.classe_id
        }