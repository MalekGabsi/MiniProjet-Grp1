#!/usr/bin/env sh
# Teste tous les endpoints d'une API déployée.
# Usage : ./test_remote.sh https://api-gestion-stages.onrender.com   (défaut : http://localhost:8000)
URL="${1:-http://localhost:8000}"
J='Content-Type: application/json'
BODY='{"nom_etudiant":"Etudiant Fictif","entreprise":"Société Exemple","intitule":"API REST","date_debut":"2026-02-01","date_fin":"2026-07-31"}'

echo "== Health";        curl -s "$URL/health"; echo
echo "== POST /stages";  R=$(curl -s -X POST "$URL/stages" -H "$J" -d "$BODY"); echo "$R"
ID=$(echo "$R" | sed -n 's/.*"id":\([0-9]*\).*/\1/p')
echo "== GET /stages";   curl -s "$URL/stages"; echo
echo "== GET /stages/$ID"; curl -s "$URL/stages/$ID"; echo
echo "== PUT /stages/$ID"; curl -s -X PUT "$URL/stages/$ID" -H "$J" -d "$(echo "$BODY" | sed 's/API REST/Stage DevOps/')"; echo
echo "== DELETE /stages/$ID"; curl -s -o /dev/null -w "HTTP %{http_code}\n" -X DELETE "$URL/stages/$ID"
echo "== GET /stages/$ID (inexistant)"; curl -s -w "  HTTP %{http_code}\n" "$URL/stages/$ID"
