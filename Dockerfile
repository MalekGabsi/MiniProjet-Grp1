# 1. Image de base officielle Python (légère)
FROM python:3.12-slim

# 2. Variables d'environnement Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DATABASE_URL=sqlite:////app/data/stages.db

# 3. Répertoire de travail
WORKDIR /app

# 4. Installation des dépendances (couche mise en cache si requirements.txt ne change pas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copie du code source
COPY app/ ./app/

# 6. Utilisateur non-root + dossier pour la base SQLite
RUN useradd --create-home appuser && mkdir -p /app/data && chown -R appuser /app/data
USER appuser

# 7. Port exposé (Render injecte sa propre variable PORT)
EXPOSE 8000

# 8. Lancement du serveur (forme shell pour lire $PORT)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
