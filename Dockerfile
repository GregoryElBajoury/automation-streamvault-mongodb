FROM python:3.11-slim

WORKDIR /app

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du script Python et du fichier de données (si nécessaire)
COPY streamvault_automation.py .
COPY livres.json .

# Commande par défaut au lancement du conteneur
CMD ["python", "streamvault_automation.py"]