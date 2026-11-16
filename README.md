# API REST – Gestion des stages

Mini-projet **Cloud Computing, Microservices & API** — Enseignante : Emna TRIGUI

API REST permettant à une école d'ingénieurs de gérer les stages de ses étudiants, développée avec **Python / FastAPI**, une base **SQLite**, conteneurisée avec **Docker** et déployée sur **Render**.

| Livrable | Emplacement |
|---|---|
| 1. Code source | ce dépôt GitHub : https://github.com/MalekGabsi/MiniProjet-Grp1 |
| 2. Dockerfile | [`Dockerfile`](Dockerfile) |
| 3. URL publique | https://api-gestion-stages.onrender.com — Swagger : https://api-gestion-stages.onrender.com/docs |
| 4. Documentation des endpoints | section [Endpoints](#endpoints) ci-dessous |
| 5. Captures d'écran | dossier [`docs/captures/`](docs/captures/) |

## Équipe (groupe de 4)

| Membre | Rôle | Tâches |
|---|---|---|
| Membre 1 – *Nom Prénom* | Développement API | `app/models.py`, `app/schemas.py`, `app/crud.py`, `app/main.py` |
| Membre 2 – *Nom Prénom* | Tests & qualité | `tests/`, collection Postman, tests Swagger, captures Partie 2 |
| Membre 3 – *Nom Prénom* | Conteneurisation | `Dockerfile`, `.dockerignore`, build/run, captures Partie 3 |
| Membre 4 – *Nom Prénom* | Déploiement Cloud & doc | GitHub, Render, `render.yaml`, README, captures Partie 4 |

---

## 1. Architecture

```
Client (navigateur / Postman / Swagger)
        │  HTTP + JSON
        ▼
┌───────────────────────── Render (Web Service, plan gratuit) ─┐
│  Conteneur Docker (python:3.12-slim)                         │
│   uvicorn ──► FastAPI (app/main.py)                          │
│                  │  validation Pydantic (schemas.py)         │
│                  ▼                                           │
│               SQLAlchemy (crud.py / models.py)               │
│                  ▼                                           │
│               SQLite  /app/data/stages.db                    │
└──────────────────────────────────────────────────────────────┘
```

```
.
├── app/
│   ├── main.py        # routes / endpoints FastAPI
│   ├── database.py    # connexion SQLite (SQLAlchemy)
│   ├── models.py      # table "stages"
│   ├── schemas.py     # validation des données (Pydantic)
│   └── crud.py        # opérations CRUD
├── tests/test_api.py  # tests automatisés (pytest)
├── postman/           # collection Postman
├── docs/captures/     # captures d'écran (livrable 5)
├── Dockerfile
├── render.yaml        # blueprint Render (optionnel)
├── test_remote.sh     # test rapide de l'API déployée
└── requirements.txt
```

## 2. Modèle de données : `Stage`

| Champ | Type | Description |
|---|---|---|
| `id` | entier | Identifiant (généré automatiquement) |
| `nom_etudiant` | texte (1–100) | Nom de l'étudiant |
| `entreprise` | texte (1–100) | Entreprise d'accueil |
| `intitule` | texte (1–200) | Intitulé du stage |
| `date_debut` | date `AAAA-MM-JJ` | Date de début |
| `date_fin` | date `AAAA-MM-JJ` | Date de fin (≥ `date_debut`) |

## Endpoints

URL de base : `http://localhost:8000` en local, ou `https://api-gestion-stages.onrender.com` dans le cloud.

| Méthode | URI | Description | Succès | Erreurs |
|---|---|---|---|---|
| GET | `/` | Message d'accueil | 200 | – |
| GET | `/health` | État du service | 200 | – |
| GET | `/stages` | Liste des stages (filtre optionnel `?entreprise=...`) | 200 | – |
| GET | `/stages/{id}` | Détail d'un stage | 200 | 404 |
| POST | `/stages` | Créer un stage | 201 | 422 |
| PUT | `/stages/{id}` | Modifier un stage (remplacement complet) | 200 | 404, 422 |
| DELETE | `/stages/{id}` | Supprimer un stage | 204 | 404 |
| GET | `/docs` | Documentation Swagger UI | 200 | – |
| GET | `/redoc` | Documentation ReDoc | 200 | – |

**Codes d'erreur**
- `404 Not Found` : le stage n'existe pas → `{"detail": "Stage introuvable (id=99)"}`
- `422 Unprocessable Entity` : champ manquant ou vide, date mal formée, ou `date_fin` antérieure à `date_debut`.

### Exemples

**Créer un stage**
```http
POST /stages
Content-Type: application/json

{
  "nom_etudiant": "Etudiant Fictif",
  "entreprise": "Société Exemple",
  "intitule": "Développement d'une API REST",
  "date_debut": "2026-02-01",
  "date_fin": "2026-07-31"
}
```
Réponse `201 Created` :
```json
{ "id": 1, "nom_etudiant": "Etudiant Fictif", "entreprise": "Société Exemple",
  "intitule": "Développement d'une API REST", "date_debut": "2026-02-01", "date_fin": "2026-07-31" }
```

**Lister** : `GET /stages` → `200` avec `[ {...}, {...} ]`

**Modifier** : `PUT /stages/1` avec le même corps que pour la création, champs modifiés → `200` avec le stage mis à jour

**Supprimer** : `DELETE /stages/1` → `204 No Content`

**Stage inexistant** : `GET /stages/999` → `404` `{"detail": "Stage introuvable (id=999)"}`

---

## 3. Lancer en local (sans Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```
Swagger : http://localhost:8000/docs

**Tests automatisés** (8 tests : création, liste, consultation, modification, suppression, 404, validation) :
```bash
pytest -v
```

## 4. Partie 2 – Tester avec Swagger / Postman

- **Swagger** : ouvrir `/docs`, déplier un endpoint, cliquer sur **Try it out** puis **Execute**.
- **Postman** : *Import* → `postman/API-Stages.postman_collection.json`, régler la variable `baseUrl`, puis lancer la collection avec **Run collection**. Les requêtes s'enchaînent ainsi : créer → lister → consulter → modifier → supprimer → 404 → 422.
- **En ligne de commande** : `./test_remote.sh http://localhost:8000`

## 5. Partie 3 – Docker

```bash
# 1. Construire l'image
docker build -t api-stages .

# 2. Lancer un conteneur
docker run -d --name api-stages -p 8000:8000 api-stages

# 3. Vérifier que l'API fonctionne
docker ps
curl http://localhost:8000/health
./test_remote.sh http://localhost:8000

# 4. Documentation Swagger
#    http://localhost:8000/docs

# Logs / arrêt
docker logs api-stages
docker stop api-stages && docker rm api-stages
```

Le `Dockerfile` part d'une image `python:3.12-slim`. Il installe d'abord les dépendances, pour profiter du cache Docker, puis copie le code. Le serveur tourne avec un utilisateur non-root et écoute sur la variable `PORT`, que Render fournit.

## 6. Partie 4 – Déploiement sur Render

1. **GitHub** : créer un dépôt public `api-gestion-stages`, puis :
   ```bash
   git init && git add . && git commit -m "API gestion des stages"
   git branch -M main
   git remote add origin https://github.com/<compte>/api-gestion-stages.git
   git push -u origin main
   ```
2. Créer un compte sur https://render.com (connexion avec GitHub).
3. **New +** → **Web Service** → connecter le dépôt GitHub.
4. Paramètres :
   - *Name* : `api-gestion-stages`
   - *Language / Runtime* : **Docker**
   - *Branch* : `main`
   - *Instance type* : **Free**
   - *Health Check Path* (Advanced) : `/health`
5. **Create Web Service** : Render construit l'image à partir du `Dockerfile`, puis la déploie.
6. Récupérer l'URL publique, de la forme `https://api-gestion-stages.onrender.com`.
7. Tester :
   - navigateur : `https://.../docs`
   - Postman : remplacer `baseUrl` par l'URL Render
   - terminal : `./test_remote.sh https://api-gestion-stages.onrender.com`

> Autre méthode : **New + → Blueprint**, puis choisir le dépôt. Render lit `render.yaml` et crée le service tout seul.

**Limites du plan gratuit** : le service se met en veille après environ 15 min d'inactivité, et la première requête suivante prend 30 à 60 s. La base SQLite est stockée dans le conteneur : elle est **réinitialisée à chaque redémarrage ou redéploiement**. En production, on utiliserait une base managée (PostgreSQL) ou un disque persistant.

## 7. Captures d'écran (`docs/captures/`)

Tests réalisés avec Swagger sur l'URL publique Render.

| # | Fichier | Contenu |
|---|---|---|
| 1 | `01-swagger-render.jpg` | Swagger UI sur `api-gestion-stages.onrender.com` : liste des endpoints |
| 2 | `02-post-201.jpg` | Création d'un stage → **201 Created** |
| 3 | `03-get-liste-200.jpg` | Liste des stages → **200 OK** |
| 4 | `04-put-200.jpg` | Modification du stage 2 → **200 OK** |
| 5 | `05-delete-204.jpg` | Suppression du stage 3 → **204 No Content** |
| 6 | `06-get-inexistant-404.jpg` | Consultation d'un stage supprimé → **404** « Stage introuvable » |
| 7 | `10-render-service-live.jpg` | Service Render : Docker, plan Free, statut **Live**, dépôt GitHub relié |
| 8 | `11-render-logs.jpg` | Logs Render (vérifications `/health` → 200) |

Partie Docker : la sortie réelle des commandes `docker build`, `docker run`, `docker ps` et `curl` est dans `07-08-docker-terminal.txt`. Captures encore à ajouter par l'équipe : terminal Docker (`07-docker.png`) et page du dépôt GitHub (`09-github.png`).

## 8. Sécurité et pistes d'amélioration

En lien avec le cours (3 piliers de la sécurité des API) :
- **Authentification** : jeton JWT ou clé d'API sur les routes POST, PUT et DELETE.
- **Autorisation** : OAuth2 avec des rôles, par exemple admin et étudiant (Keycloak).
- **Traçabilité** : journaliser les requêtes (qui, quoi, quand).
- **Persistance** : remplacer SQLite par PostgreSQL managé.
- **CI/CD** : GitHub Actions qui lance `pytest` avant chaque déploiement automatique sur Render.

> Projet pédagogique : seules des données fictives sont utilisées.
