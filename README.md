# API REST – Gestion des stages

Mini-projet **Cloud Computing, Microservices & API** — Enseignante : Emna TRIGUI

API REST permettant à une école d'ingénieurs de gérer les stages de ses étudiants, développée avec **Python / FastAPI**, une base **SQLite**, conteneurisée avec **Docker** et déployée sur **Render**.

| Livrable | Emplacement |
|---|---|
| 1. Code source | ce dépôt GitHub : `https://github.com/<compte>/api-gestion-stages` |
| 2. Dockerfile | [`Dockerfile`](Dockerfile) |
| 3. URL publique | `https://<nom-du-service>.onrender.com` — Swagger : `/docs` |
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

URL de base : `http://localhost:8000` en local, ou `https://<nom-du-service>.onrender.com` dans le cloud.

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
6. Récupérer l'URL publique, de la forme `https://api-gestion-stages-xxxx.onrender.com`.
7. Tester :
   - navigateur : `https://.../docs`
   - Postman : remplacer `baseUrl` par l'URL Render
   - terminal : `./test_remote.sh https://api-gestion-stages-xxxx.onrender.com`

> Autre méthode : **New + → Blueprint**, puis choisir le dépôt. Render lit `render.yaml` et crée le service tout seul.

**Limites du plan gratuit** : le service se met en veille après environ 15 min d'inactivité, et la première requête suivante prend 30 à 60 s. La base SQLite est stockée dans le conteneur : elle est **réinitialisée à chaque redémarrage ou redéploiement**. En production, on utiliserait une base managée (PostgreSQL) ou un disque persistant.

## 7. Captures d'écran à fournir (`docs/captures/`)

| # | Fichier conseillé | Contenu |
|---|---|---|
| 1 | `01-swagger-local.png` | Swagger UI listant les endpoints |
| 2 | `02-post-201.png` | Création d'un stage (201) |
| 3 | `03-get-liste.png` | Liste des stages |
| 4 | `04-put-200.png` | Modification d'un stage |
| 5 | `05-delete-204.png` | Suppression |
| 6 | `06-get-404.png` | Stage inexistant (404) |
| 7 | `07-docker-build.png` | `docker build` réussi |
| 8 | `08-docker-ps.png` | `docker ps` avec le conteneur, et `curl /health` |
| 9 | `09-github.png` | Dépôt GitHub |
| 10 | `10-render-deploy.png` | Logs Render « Your service is live » |
| 11 | `11-render-swagger.png` | Swagger ouvert depuis l'URL publique `onrender.com` |
| 12 | `12-postman-runner.png` | Postman Runner avec tous les tests en vert sur l'URL Render |

## 8. Sécurité et pistes d'amélioration

En lien avec le cours (3 piliers de la sécurité des API) :
- **Authentification** : jeton JWT ou clé d'API sur les routes POST, PUT et DELETE.
- **Autorisation** : OAuth2 avec des rôles, par exemple admin et étudiant (Keycloak).
- **Traçabilité** : journaliser les requêtes (qui, quoi, quand).
- **Persistance** : remplacer SQLite par PostgreSQL managé.
- **CI/CD** : GitHub Actions qui lance `pytest` avant chaque déploiement automatique sur Render.

> Projet pédagogique : seules des données fictives sont utilisées.
