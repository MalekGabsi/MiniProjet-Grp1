"""Opérations CRUD sur la table `stages`."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas


def lister_stages(db: Session, entreprise: str | None = None) -> list[models.Stage]:
    requete = select(models.Stage).order_by(models.Stage.id)
    if entreprise:
        requete = requete.where(models.Stage.entreprise.ilike(f"%{entreprise}%"))
    return list(db.scalars(requete))


def obtenir_stage(db: Session, stage_id: int) -> models.Stage | None:
    return db.get(models.Stage, stage_id)


def creer_stage(db: Session, donnees: schemas.StageCreate) -> models.Stage:
    stage = models.Stage(**donnees.model_dump())
    db.add(stage)
    db.commit()
    db.refresh(stage)
    return stage


def modifier_stage(db: Session, stage: models.Stage, donnees: schemas.StageUpdate) -> models.Stage:
    for champ, valeur in donnees.model_dump().items():
        setattr(stage, champ, valeur)
    db.commit()
    db.refresh(stage)
    return stage


def supprimer_stage(db: Session, stage: models.Stage) -> None:
    db.delete(stage)
    db.commit()
