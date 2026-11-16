"""Tests automatisés des endpoints (pytest + TestClient)."""
import os

os.environ["DATABASE_URL"] = "sqlite:///./test_stages.db"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

STAGE = {
    "nom_etudiant": "Etudiant Test",
    "entreprise": "Entreprise Fictive",
    "intitule": "Développement API REST",
    "date_debut": "2026-02-01",
    "date_fin": "2026-07-31",
}


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def test_accueil_et_health(client):
    assert client.get("/").status_code == 200
    assert client.get("/health").json() == {"status": "ok"}


def test_creation_stage(client):
    r = client.post("/stages", json=STAGE)
    assert r.status_code == 201
    data = r.json()
    assert data["id"] == 1
    assert data["entreprise"] == STAGE["entreprise"]


def test_liste_stages(client):
    client.post("/stages", json=STAGE)
    client.post("/stages", json={**STAGE, "entreprise": "Autre Société"})
    r = client.get("/stages")
    assert r.status_code == 200
    assert len(r.json()) == 2
    assert len(client.get("/stages", params={"entreprise": "autre"}).json()) == 1


def test_consultation_stage(client):
    sid = client.post("/stages", json=STAGE).json()["id"]
    r = client.get(f"/stages/{sid}")
    assert r.status_code == 200
    assert r.json()["nom_etudiant"] == STAGE["nom_etudiant"]


def test_modification_stage(client):
    sid = client.post("/stages", json=STAGE).json()["id"]
    r = client.put(f"/stages/{sid}", json={**STAGE, "intitule": "Stage DevOps"})
    assert r.status_code == 200
    assert r.json()["intitule"] == "Stage DevOps"


def test_suppression_stage(client):
    sid = client.post("/stages", json=STAGE).json()["id"]
    assert client.delete(f"/stages/{sid}").status_code == 204
    assert client.get(f"/stages/{sid}").status_code == 404


def test_stage_inexistant(client):
    assert client.get("/stages/999").status_code == 404
    assert client.put("/stages/999", json=STAGE).status_code == 404
    assert client.delete("/stages/999").status_code == 404
    assert "introuvable" in client.get("/stages/999").json()["detail"]


def test_validation_dates_et_champs(client):
    assert client.post("/stages", json={**STAGE, "date_fin": "2026-01-01"}).status_code == 422
    assert client.post("/stages", json={**STAGE, "nom_etudiant": ""}).status_code == 422
    incomplet = {k: v for k, v in STAGE.items() if k != "entreprise"}
    assert client.post("/stages", json=incomplet).status_code == 422
