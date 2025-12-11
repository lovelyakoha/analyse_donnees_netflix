# Analyse Exploratoire du Catalogue Netflix

Ce projet propose une analyse exploratoire complète (EDA) et un tableau de bord interactif des données Netflix.
Réalisé dans le cadre du cours **8PRO408 - Outils de programmation pour la science des données**.

Dataset: [https://www.kaggle.com/datasets/shivamb/netflix-shows](https://www.kaggle.com/datasets/shivamb/netflix-shows)

## Structure du projet
- `data/` : Contient le jeu de données (`netflix_titles.csv`).
- `notebooks/` : Contient le notebook Jupyter d'analyse exploratoire.
- `app/` : Contient le code de l'application Streamlit.
- `requirements.txt` : Liste des dépendances Python.

## Comment lancer le projet

### 1. Cloner le dépôt
```bash
git clone https://github.com/lovelyakoha/analyse_donnees_netflix.git
```

### 2. Naviguer vers le dossier
`cd analyse_donnees_netflix`

### 3. Installer les dépendances
`pip install -r requirements.txt`

### 4. Lancer streamlit
`streamlit run app/app.py`