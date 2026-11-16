"""API REST de gestion des stages - FastAPI + SQLite."""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from . import crud, schemas
from .database import Base, engine, get_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Création des tables au démarrage (base SQLite vide sur Render après redéploiement)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="API Gestion des Stages",
    description=(
        "API REST permettant à une école d'ingénieurs de gérer les stages de ses étudiants.\n\n"
        "Mini-projet *Cloud Computing, Microservices & API* — FastAPI, SQLite, Docker, Render."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

MSG_INTROUVABLE = "Stage introuvable"


def _stage_ou_404(db: Session, stage_id: int):
    stage = crud.obtenir_stage(db, stage_id)
    if stage is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{MSG_INTROUVABLE} (id={stage_id})")
    return stage


@app.get("/", tags=["Infos"], summary="Page d'accueil de l'API")
def accueil():
    return {
        "message": "Bienvenue sur l'API de gestion des stages",
        "documentation": "/docs",
        "endpoints": "/stages",
    }


@app.get("/health", tags=["Infos"], summary="Vérification de l'état du service")
def health():
    return {"status": "ok"}


@app.get("/stages", response_model=list[schemas.StageRead], tags=["Stages"],
         summary="Lister tous les stages")
def lister_stages(
    entreprise: str | None = Query(None, description="Filtrer par entreprise (recherche partielle)"),
    db: Session = Depends(get_db),
):
    return crud.lister_stages(db, entreprise)


@app.get("/stages/{stage_id}", response_model=schemas.StageRead, tags=["Stages"],
         summary="Consulter un stage", responses={404: {"description": MSG_INTROUVABLE}})
def obtenir_stage(stage_id: int, db: Session = Depends(get_db)):
    return _stage_ou_404(db, stage_id)


@app.post("/stages", response_model=schemas.StageRead, status_code=status.HTTP_201_CREATED,
          tags=["Stages"], summary="Créer un stage")
def creer_stage(donnees: schemas.StageCreate, db: Session = Depends(get_db)):
    return crud.creer_stage(db, donnees)


@app.put("/stages/{stage_id}", response_model=schemas.StageRead, tags=["Stages"],
         summary="Modifier un stage", responses={404: {"description": MSG_INTROUVABLE}})
def modifier_stage(stage_id: int, donnees: schemas.StageUpdate, db: Session = Depends(get_db)):
    stage = _stage_ou_404(db, stage_id)
    return crud.modifier_stage(db, stage, donnees)


@app.delete("/stages/{stage_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Stages"],
            summary="Supprimer un stage", responses={404: {"description": MSG_INTROUVABLE}})
def supprimer_stage(stage_id: int, db: Session = Depends(get_db)):
    stage = _stage_ou_404(db, stage_id)
    crud.supprimer_stage(db, stage)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
