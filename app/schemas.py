"""Schémas Pydantic : validation des entrées / sorties JSON."""
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StageBase(BaseModel):
    nom_etudiant: str = Field(..., min_length=1, max_length=100, examples=["Ahmed Ben Salah"])
    entreprise: str = Field(..., min_length=1, max_length=100, examples=["Sopra Steria"])
    intitule: str = Field(..., min_length=1, max_length=200, examples=["Développement d'une API REST"])
    date_debut: date = Field(..., examples=["2026-02-01"])
    date_fin: date = Field(..., examples=["2026-07-31"])

    @model_validator(mode="after")
    def verifier_dates(self):
        if self.date_fin < self.date_debut:
            raise ValueError("date_fin doit être postérieure ou égale à date_debut")
        return self


class StageCreate(StageBase):
    """Corps attendu pour POST /stages."""


class StageUpdate(StageBase):
    """Corps attendu pour PUT /stages/{id} (remplacement complet)."""


class StageRead(StageBase):
    """Représentation renvoyée par l'API."""
    model_config = ConfigDict(from_attributes=True)

    id: int
