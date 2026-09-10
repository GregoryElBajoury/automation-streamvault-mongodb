#  Automation StreamVault MongoDB to OWL Ontology Pipeline

> *Transformation automatisée de structures NoSQL (MongoDB) en modèles sémantiques normalisés (RDF/OWL) propulsée par Python, Docker et le Web Sémantique.*

---

##  Contexte du Projet

Dans le cadre de projets Big Data et de la plateforme **StreamVault**, l'un des défis majeurs réside dans l'interopérabilité et la structuration des données hétérogènes stockées dans des bases NoSQL (MongoDB). 

Ce projet propose un pipeline automatisé capable d'injecter un jeu de données initial (`livres.json`) dans MongoDB, d'inspecter dynamiquement la collection, d'analyser son schématisme à la volée, et de générer un graphe de connaissances normalisé au format OWL (`.owl`), exploitable par des moteurs de raisonnement sémantique.

---

##  Stack Technique

* **Langage :** Python (avec `rdflib`, `pymongo`)
* **Base de données :** MongoDB
* **Conteneurisation :** Docker & Docker Compose
* **Standards :** RDF, OWL, Web Sémantique

---

##  Architecture du Projet

```text
automation-streamvault-mongodb/
├── .env                              # Configuration locale (ignorée par Git)
├── .gitignore                        # Fichiers exclus du versioning
├── Dockerfile                        # Configuration de l'environnement d'exécution Python
├── docker-compose.yml                # Orchestration des services (MongoDB + Pipeline)
├── livres.json                       # Données de test initiales
├── requirements.txt                  # Dépendances Python (pymongo, rdflib, etc.)
├── streamvault_automation.py         # Script principal d'extraction et de conversion sémantique
└── README.md                         # Documentation du projet
```

## Guide d'Utilisation rapide

1. Prérequis

S'assurer d'avoir Docker et Docker Compose installés sur ta machine.

3. Configuration de l'environnement


Dupliquer le fichier d'exemple pour créer son propre fichier de configuration `.env` :

```bash
cp .env.example .env
```

3. Lancement du Pipeline via Docker

   
Exécute le conteneur pour lancer l'analyse de la base MongoDB et générer le fichier d'ontologie :

```bash
docker compose up --build
```

Le fichier de sortie `.owl` généré sera automatiquement versé dans le répertoire de travail, prêt à être visualisé (par exemple via WebVOWL).



Auteur
Gregory El Bajoury
Junior DevOps & Data Engineer

Nexus DevOps



