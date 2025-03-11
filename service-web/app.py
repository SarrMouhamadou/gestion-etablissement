from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import requests
import bcrypt


app = Flask(__name__)

# Définir la clé secrète pour la gestion des sessions
app.secret_key = '12345'  # Remplacez par une clé secrète unique


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:passer@localhost:5432/dbweb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de la base de données après la configuration
db = SQLAlchemy(app)


login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirige vers la page de login si non connecté
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
login_manager.login_message_category = "warning"


# URL des microservices
BASE_URLS = {
    'etudiants': 'http://127.0.0.1:5000',
    'classes': 'http://127.0.0.1:5002',
    'profs': 'http://127.0.0.1:5003',
    'cours': 'http://127.0.0.1:5004',
    'emplois': 'http://127.0.0.1:5005'
}


# Charger un utilisateur pour Flask-Login
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route pour la page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # Redirige si déjà connecté
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)
            flash('Connexion réussie !', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nom d’utilisateur ou mot de passe incorrect.', 'danger')
    
    return render_template('login.html')

# Route pour la déconnexion
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'success')
    return redirect(url_for('login'))


# Fonctions pour récupérer les options dynamiques
def get_classes():
    response = requests.get(f"{BASE_URLS['classes']}/classes")
    return response.json() if response.status_code == 200 else []

def get_profs():
    response = requests.get(f"{BASE_URLS['profs']}/professeurs")
    return response.json() if response.status_code == 200 else []

def get_cours():
    response = requests.get(f"{BASE_URLS['cours']}/cours")
    return response.json() if response.status_code == 200 else []

# Page d'accueil
# Page d'accueil protégée
@app.route('/')
@login_required
def index():
    stats = {
        'total_etudiants': len(requests.get(f"{BASE_URLS['etudiants']}/etudiants").json()),
        'total_profs': len(requests.get(f"{BASE_URLS['profs']}/professeurs").json()),
        'total_classes': len(requests.get(f"{BASE_URLS['classes']}/classes").json()),
        'total_cours': len(requests.get(f"{BASE_URLS['cours']}/cours").json()),
        'total_emplois': len(requests.get(f"{BASE_URLS['emplois']}/emplois").json())
    }
    
    response_emplois = requests.get(f"{BASE_URLS['emplois']}/emplois")  # Supprimer le filtre par date
    emplois = []
    if response_emplois.status_code == 200:
        all_emplois = response_emplois.json()
        classes = {c['id']: c['nom'] for c in requests.get(f"{BASE_URLS['classes']}/classes").json() if requests.get(f"{BASE_URLS['classes']}/classes").status_code == 200}
        cours = {c['id']: c['nom'] for c in requests.get(f"{BASE_URLS['cours']}/cours").json() if requests.get(f"{BASE_URLS['cours']}/cours").status_code == 200}
        profs = {p['matricule']: f"{p['nom']} {p['prenom']}" for p in requests.get(f"{BASE_URLS['profs']}/professeurs").json() if requests.get(f"{BASE_URLS['profs']}/professeurs").status_code == 200}
        for e in all_emplois:
            e['classe_nom'] = classes.get(e['classe_id'], 'Inconnu')
            e['cours_titre'] = cours.get(e['cours_id'], 'Inconnu')
            e['professeur_nom'] = profs.get(e['professeur_matricule'], 'Inconnu')
            emplois.append(e)

    return render_template('index.html', stats=stats, emplois=emplois)

# Route pour les paramètres (modification des données de l'utilisateur)
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_username = request.form['new_username']
        new_password = request.form['new_password']

        user = User.query.get(current_user.id)
        if user and bcrypt.checkpw(current_password.encode('utf-8'), user.password.encode('utf-8')):
            if new_username:
                user.username = new_username
            if new_password:
                user.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            db.session.commit()
            flash('Profil mis à jour avec succès !', 'success')
            return redirect(url_for('index'))
        else:
            flash('Mot de passe actuel incorrect.', 'danger')
    
    return render_template('settings.html')

# Étudiants
@app.route('/etudiants')
@login_required
def list_etudiants():
    response = requests.get(f"{BASE_URLS['etudiants']}/etudiants")
    if response.status_code == 200:
        etudiants = response.json()
        print("Données des étudiants:", etudiants)  # Ajout pour déboguer
        # Récupérer les classes
        response_classes = requests.get(f"{BASE_URLS['classes']}/classes")
        if response_classes.status_code == 200:
            classes = {classe['id']: classe['nom'] for classe in response_classes.json()}
            print("Dictionnaire des classes:", classes)  # Ajout pour déboguer
            # Ajouter le nom de la classe à chaque étudiant
            for e in etudiants:
                e['classe_nom'] = classes.get(e.get('classe_id', ''), 'Inconnu')  # Utilisation de .get() pour éviter KeyError
            return render_template('etudiants_list.html', etudiants=etudiants)
    return f"Erreur: {response.text}", 500

@app.route('/etudiant/add', methods=['GET', 'POST'])
@login_required
def add_etudiant():
    if request.method == 'POST':
        data = {
            'matricule': request.form['matricule'],
            'nom': request.form['nom'],
            'prenom': request.form['prenom'],
            'email': request.form['email'],
            'classe_id': request.form['classe_id']
        }
        response = requests.post(f"{BASE_URLS['etudiants']}/etudiants", json=data)
        if response.status_code == 201:
            flash('Etudiant ajouté avec succès !', 'success')
            return redirect(url_for('list_etudiants'))
        else:
            flash(f"Erreur lors de l'ajout d'un étudiant : {response.text}", 'danger')
        return redirect(url_for('list_etudiants'))
    classes = get_classes()
    return render_template('etudiant_form.html', classes=classes)

@app.route('/etudiant/edit/<matricule>', methods=['GET', 'POST'])
@login_required
def edit_etudiant(matricule):
    if request.method == 'POST':
        data = {
            'matricule': request.form['matricule'],
            'nom': request.form['nom'],
            'prenom': request.form['prenom'],
            'email': request.form['email'],
            'classe_id': request.form['classe_id']
        }
        response = requests.put(f"{BASE_URLS['etudiants']}/etudiants/{matricule}", json=data)
        if response.status_code == 200:
            flash('Etudiant modifié avec succès !', 'success')
            return redirect(url_for('list_etudiants'))
        flash(f"Erreur : {response.text}", 'danger')
        return redirect(url_for('list_etudiants'))
    response = requests.get(f"{BASE_URLS['etudiants']}/etudiants/{matricule}")
    if response.status_code == 200:
        etudiant = response.json()
        classes = get_classes()
        return render_template('etudiant_form.html', etudiant=etudiant, classes=classes)
    return f"Erreur: {response.text}", 500

@app.route('/etudiant/delete/<matricule>')
@login_required
def delete_etudiant(matricule):
    response = requests.delete(f"{BASE_URLS['etudiants']}/etudiants/{matricule}")
    if response.status_code == 204:
        flash('Etudiant supprimé avec succès !', 'success')
        return redirect(url_for('list_etudiants'))
    flash(f"Erreur : {response.text}", 'danger')
    return redirect(url_for('list_etudiants'))

# Classes
@app.route('/classes')
@login_required
def list_classes():
    response = requests.get(f"{BASE_URLS['classes']}/classes")
    if response.status_code == 200:
        classes = response.json()
        return render_template('classes_list.html', classes=classes)
    return f"Erreur: {response.text}", 500

@app.route('/classe/add', methods=['GET', 'POST'])
@login_required
def add_classe():
    if request.method == 'POST':
        data = {
            'id': request.form['id'],
            'nom': request.form['nom']
        }
        response = requests.post(f"{BASE_URLS['classes']}/classes", json=data)
        if response.status_code == 201:
            flash('Classe ajoutée avec succès !', 'success')
            return redirect(url_for('list_classes'))
        flash(f"Erreur : {response.text}", 'danger')
    return render_template('classe_form.html')

@app.route('/classe/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_classe(id):
    if request.method == 'POST':
        data = {
            'id': request.form['id'],
            'nom': request.form['nom']
        }
        response = requests.put(f"{BASE_URLS['classes']}/classes/{id}", json=data)
        if response.status_code == 200:
            flash('Classe modifiée avec succès !', 'success')
            return redirect(url_for('list_classes'))
        flash(f"Erreur : {response.text}", 'danger')
    response = requests.get(f"{BASE_URLS['classes']}/classes/{id}")
    if response.status_code == 200:
        classe = response.json()
        return render_template('classe_form.html', classe=classe)
    return f"Erreur: {response.text}", 500

@app.route('/classe/delete/<id>')
@login_required
def delete_classe(id):
    response = requests.delete(f"{BASE_URLS['classes']}/classes/{id}")
    if response.status_code == 204:
        flash('Classe supprimée avec succès !', 'success')
        return redirect(url_for('list_classes'))
    flash(f"Erreur : {response.text}", 'danger')
    return redirect(url_for('list_classes'))

# Professeurs
@app.route('/profs')
@login_required
def list_profs():
    response = requests.get(f"{BASE_URLS['profs']}/professeurs")
    if response.status_code == 200:
        profs = response.json()
        # Récupérer les cours pour associer les titres aux professeurs
        response_cours = requests.get(f"{BASE_URLS['cours']}/cours")
        if response_cours.status_code == 200:
            cours = {cours['id']: cours['nom'] for cours in response_cours.json()}
            # Ajouter le nom de la matière à chaque professeur
            for prof in profs:
                matiere_id = prof.get('matiere')  # Récupère l'ID de la matière
                prof['matiere_titre'] = cours.get(matiere_id, 'Inconnu') if matiere_id else 'Non assigné'
            return render_template('profs_list.html', profs=profs)
        flash("Erreur : Impossible de récupérer les cours", 'danger')
        return render_template('profs_list.html', profs=profs)
    return f"Erreur: {response.text}", 500

#@app.route('/profs')
#def list_profs():
#    response = requests.get(f"{BASE_URLS['profs']}/professeurs")
#    if response.status_code == 200:
#        profs = response.json()
#        for prof in profs:
#            prof['matiere_titre'] = prof.get('matiere', 'Inconnu')  # Utilise directement matiere
#        return render_template('profs_list.html', profs=profs)
 #   return f"Erreur: {response.text}", 500

@app.route('/prof/add', methods=['GET', 'POST'])
@login_required
def add_prof():
    # Récupère la liste des cours
    response = requests.get(f"{BASE_URLS['cours']}/cours")  # Assure-toi que l'URL est correcte
    if response.status_code == 200:
        cours = response.json()  # Liste des cours

        if request.method == 'POST':
            data = {
                'matricule': request.form['matricule'],
                'nom': request.form['nom'],
                'prenom': request.form['prenom'],
                'email': request.form['email'],
                'matiere': request.form['matiere']  # Ceci sera l'ID du cours sélectionné
            }
            response = requests.post(f"{BASE_URLS['profs']}/professeurs", json=data)
            if response.status_code == 201:
                flash('Professeur ajouté avec succès !', 'success')
                return redirect(url_for('list_profs'))
            flash(f"Erreur : {response.text}", 'danger')
        return render_template('prof_form.html', cours=cours)  # Passe la liste des cours au template

    flash(f"Erreur : {response.text}", 'danger')
    return redirect(url_for('list_profs'))

@app.route('/prof/edit/<matricule>', methods=['GET', 'POST'])
@login_required
def edit_prof(matricule):
    # Récupère la liste des cours
    response_cours = requests.get(f"{BASE_URLS['cours']}/cours")
    if response_cours.status_code == 200:
        cours = response_cours.json()

        if request.method == 'POST':
            data = {
                'matricule': request.form['matricule'],
                'nom': request.form['nom'],
                'prenom': request.form['prenom'],
                'email': request.form['email'],
                'matiere': request.form['matiere']
            }
            response = requests.put(f"{BASE_URLS['profs']}/professeurs/{matricule}", json=data)
            if response.status_code == 200:
                flash('Professeur modifié avec succès !', 'success')
                return redirect(url_for('list_profs'))
            flash(f"Erreur : {response.text}", 'danger')

        response_prof = requests.get(f"{BASE_URLS['profs']}/professeurs/{matricule}")
        if response_prof.status_code == 200:
            prof = response_prof.json()
            return render_template('prof_form.html', prof=prof, cours=cours)  # Passe le professeur et les cours au template

    flash(f"Erreur : {response_cours.text}", 'danger')
    return redirect(url_for('list_profs'))

@app.route('/prof/delete/<matricule>')
@login_required
def delete_prof(matricule):
    response = requests.delete(f"{BASE_URLS['profs']}/professeurs/{matricule}")
    if response.status_code == 204:
        flash('Professeur supprimé avec succès !', 'success')
        return redirect(url_for('list_profs'))
    flash(f"Erreur : {response.text}", 'danger')
    return redirect(url_for('list_profs'))

# Cours
@app.route('/cours')
@login_required
def list_cours():
    response = requests.get(f"{BASE_URLS['cours']}/cours")
    if response.status_code == 200:
        cours = response.json()
        # Récupérer la liste des professeurs
        response_profs = requests.get(f"{BASE_URLS['profs']}/professeurs")
        if response_profs.status_code == 200:
            profs = {prof['matricule']: f"{prof['nom']} {prof['prenom']}" for prof in response_profs.json()}
            # Ajouter le nom du professeur à chaque cours
            for c in cours:
                c['professeur_nom'] = profs.get(c['professeur_matricule'], 'Inconnu')
            return render_template('cours_list.html', cours=cours)
    return f"Erreur: {response.text}", 500

@app.route('/cours/add', methods=['GET', 'POST'])
@login_required
def add_cours():
    if request.method == 'POST':
        data = {
            'nom': request.form['nom'],
            'description': request.form['description']
        }
        response = requests.post(f"{BASE_URLS['cours']}/cours", json=data)
        if response.status_code == 201:
            flash('Cours ajouté avec succès !', 'success')
            return redirect(url_for('list_cours'))
        flash(f"Erreur : {response.text}", 'danger')
    return render_template('cours_form.html')

@app.route('/cours/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_cours(id):
    if request.method == 'POST':
        data = {
            'nom': request.form['nom'],
            'description': request.form['description']
        }
        response = requests.put(f"{BASE_URLS['cours']}/cours/{id}", json=data)
        if response.status_code == 200:
            flash('Cours modifié avec succès !', 'success')
            return redirect(url_for('list_cours'))
        flash(f"Erreur : {response.text}", 'danger')
    response = requests.get(f"{BASE_URLS['cours']}/cours/{id}")
    if response.status_code == 200:
        cours = response.json()
        return render_template('cours_form.html', cours=cours)
    return f"Erreur: {response.text}", 500

@app.route('/cours/delete/<int:id>')
@login_required
def delete_cours(id):
    response = requests.delete(f"{BASE_URLS['cours']}/cours/{id}")
    if response.status_code == 204:
        flash('Cours supprimé avec succès !', 'success')
        return redirect(url_for('list_cours'))
    flash(f"Erreur : {response.text}", 'danger')
    return redirect(url_for('list_cours'))

# Emplois du temps
@app.route('/emplois')
@login_required
def list_emplois():
    response = requests.get(f"{BASE_URLS['emplois']}/emplois")
    if response.status_code == 200:
        emplois = response.json()
        # Récupérer les cours
        response_cours = requests.get(f"{BASE_URLS['cours']}/cours")
        cours_dict = {cours['id']: cours['nom'] for cours in response_cours.json()} if response_cours.status_code == 200 else {}
        # Récupérer les professeurs
        response_profs = requests.get(f"{BASE_URLS['profs']}/professeurs")
        profs_dict = {prof['matricule']: f"{prof['nom']} {prof['prenom']}" for prof in response_profs.json()} if response_profs.status_code == 200 else {}
        # Récupérer les classes
        response_classes = requests.get(f"{BASE_URLS['classes']}/classes")
        classes_dict = {classe['id']: classe['nom'] for classe in response_classes.json()} if response_classes.status_code == 200 else {}
        # Ajouter les noms aux emplois
        for e in emplois:
            e['cours_titre'] = cours_dict.get(e['cours_id'], 'Inconnu')
            e['professeur_nom'] = profs_dict.get(e['professeur_matricule'], 'Inconnu')
            e['classe_nom'] = classes_dict.get(e['classe_id'], 'Inconnu')
        return render_template('emplois_list.html', emplois=emplois)
    return f"Erreur: {response.text}", 500

@app.route('/emploi/add', methods=['GET', 'POST'])
@login_required
def add_emploi():
    response_cours = requests.get(f"{BASE_URLS['cours']}/cours")
    response_profs = requests.get(f"{BASE_URLS['profs']}/professeurs")
    response_classes = requests.get(f"{BASE_URLS['classes']}/classes")
    
    if response_cours.status_code == 200 and response_profs.status_code == 200 and response_classes.status_code == 200:
        cours = response_cours.json()
        profs = response_profs.json()
        classes = response_classes.json()
        
        if request.method == 'POST':
            data = {
                'date': request.form['date'],
                'heure': request.form['heure'],
                'cours_id': int(request.form['cours_id']),
                'professeur_matricule': request.form['professeur_matricule'],
                'classe_id': request.form['classe_id']
            }
            response = requests.post(f"{BASE_URLS['emplois']}/emplois", json=data)
            if response.status_code == 201:
                flash('Emploi du temps ajouté avec succès !', 'success')
                return redirect(url_for('list_emplois'))
            flash(f"Erreur : {response.text}", 'danger')
        
        today = datetime.now().strftime('%Y-%m-%d')  # Prérempli avec aujourd'hui
        return render_template('emploi_form.html', cours=cours, profs=profs, classes=classes, today=today)
    flash('Erreur lors de la récupération des données nécessaires.', 'danger')
    return redirect(url_for('list_emplois'))

@app.route('/emploi/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_emploi(id):
    if request.method == 'POST':
        data = {
            'date': request.form['date'],
            'heure': request.form['heure'],
            'cours_id': int(request.form['cours_id']),
            'professeur_matricule': request.form['professeur_matricule'],
            'classe_id': request.form['classe_id']
        }
        response = requests.put(f"{BASE_URLS['emplois']}/emplois/{id}", json=data)
        if response.status_code == 200:
            flash('Emploi modifié avec succès !', 'success')
            return redirect(url_for('list_emplois'))
        flash(f"Erreur : {response.text}", 'danger')
    response = requests.get(f"{BASE_URLS['emplois']}/emplois/{id}")
    if response.status_code == 200:
        emploi = response.json()
        classes = get_classes()
        profs = get_profs()
        cours = get_cours()
        return render_template('emploi_form.html', emploi=emploi, classes=classes, profs=profs, cours=cours)
    return f"Erreur: {response.text}", 500

@app.route('/emploi/delete/<int:id>')
@login_required
def delete_emploi(id):
    response = requests.delete(f"{BASE_URLS['emplois']}/emplois/{id}")
    if response.status_code == 204:
        flash('Emploi supprimé avec succès !', 'success')
        return redirect(url_for('list_emplois'))
    flash(f"Erreur : {response.text}", 'danger')
    return redirect(url_for('list_emplois'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Créer un utilisateur par défaut (admin:admin)
        if not User.query.filter_by(username='admin').first():
            hashed_password = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin_user = User(username='admin', password=hashed_password)
            db.session.add(admin_user)
            db.session.commit()
            print("Utilisateur par défaut créé : admin/admin")
    print("Démarrage du serveur Flask pour service-web...")
    app.run(port=5006, debug=True)
