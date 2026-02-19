#!/bin/bash

echo "🚀 Démarrage rapide du projet Project Management"

# Copier le fichier d'environnement
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Fichier .env créé"
fi

# Construire et démarrer les conteneurs Docker
echo "🐳 Démarrage des conteneurs Docker..."
docker-compose up -d --build

# Attendre que les conteneurs soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 5

# Appliquer les migrations
echo "📦 Application des migrations..."
docker-compose exec web python manage.py makemigrations utilisateurs
docker-compose exec web python manage.py makemigrations taches
docker-compose exec web python manage.py migrate

# Créer un superutilisateur
echo "👤 Création du superutilisateur..."
docker-compose exec web python manage.py createsuperuser

# Collecter les fichiers statiques
echo "📁 Collecte des fichiers statiques..."
docker-compose exec web python manage.py collectstatic --noinput

echo ""
echo "✅ Installation terminée!"
echo "🌐 Application disponible sur: http://localhost:8000"
echo "🔑 Admin disponible sur: http://localhost:8000/admin"
echo ""
echo "Commandes utiles:"
echo "  - Voir les logs: docker-compose logs -f"
echo "  - Arrêter: docker-compose down"
echo "  - Redémarrer: docker-compose restart"
