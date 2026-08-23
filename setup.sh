#!/bin/bash
set -e

echo "Installing dependencies"
poetry install

if [ ! -f .env ]; then
    echo "Creating .env."
    cp .env.template .env
fi

if [ ! -f certs/private.pem ]; then
    echo "Generating JWT keys"
    mkdir -p certs
    openssl genrsa -out certs/private.pem 2048
    openssl rsa -in certs/private.pem -pubout -out certs/public.pem
fi

echo "Starting Database in Docker..."
docker compose up -d pg

echo "Waiting for PostgreSQL to become healthy."
until [ "$(docker inspect -f '{{.State.Health.Status}}' task-tracker-pg-1)" == "healthy" ]; do
    echo "Postgres is initializing..."
    sleep 2
done
echo "Postgres is READY!"

echo "Running migrations"
poetry run alembic upgrade head

echo "Seeding admin user"
poetry run python -m scripts.create_admin

echo "READY! Run: poetry run python main.py"
echo "Login with admin / admin for full access."