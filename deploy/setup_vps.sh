#!/usr/bin/env bash
# ============================================================================
# CNMOVI — 1-CLICK UBUNTU/DEBIAN VPS DEPLOYMENT SCRIPT
# Runs 24/7/365 without stopping!
# ============================================================================

set -e

echo "=== [1/4] Tizim yangilanmoqda va Docker o'rnatilmoqda ==="
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg git

if ! command -v docker &> /dev/null; then
    echo "Docker o'rnatilmoqda..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

echo "=== [2/4] Loyiha konteyneri yig'ilmoqda (Docker Build) ==="
docker compose down || true
docker compose build

echo "=== [3/4] CNMOVI 24/7 Rejimda ishga tushirilmoqda ==="
docker compose up -d

echo "=== [4/4] Tekshiruv ==="
docker ps

echo "======================================================================"
echo "Tabriklaymiz! CNMOVI boti va kinoteatri 24/7 uzluksiz ishga tushdi!"
echo "Endi kompyuteringizni o'chirib qo'ysangiz ham bot to'xtamasdan ishlaydi."
echo "======================================================================"
