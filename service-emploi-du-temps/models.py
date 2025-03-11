from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Date, Time

db = SQLAlchemy()

class EmploiDuTemps(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    heure = db.Column(db.Time, nullable=False)
    cours_id = db.Column(db.Integer, nullable=False)
    professeur_matricule = db.Column(db.String(20), nullable=False)  # Correction
    classe_id = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'heure': self.heure.strftime('%H:%M'),  # Format HH:MM (ex: "14:00")
            'cours_id': self.cours_id,
            'professeur_matricule': self.professeur_matricule,
            'classe_id': self.classe_id
        }