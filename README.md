# E-Learning Management System

## 1. Description du projet

E-Learning Management System est une application web permettant la gestion complète d'une plateforme d'apprentissage en ligne.

La plateforme permet :

- aux administrateurs de gérer les utilisateurs, les cours et les statistiques ;
- aux enseignants de créer des cours, leçons, quiz et devoirs ;
- aux étudiants de s'inscrire aux cours, suivre leur progression, passer les quiz, soumettre les devoirs et obtenir des certificats.

## 2. Technologies utilisées

### Backend

- Python
- Django
- Django REST Framework
- JWT Authentication
- MySQL

### Frontend

- Vue.js
- Axios / Fetch API
- Chart.js
- CSS

## 3. Installation du projet

### Backend Django

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver