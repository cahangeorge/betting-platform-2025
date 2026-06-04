#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

if ! docker compose ps postgres | grep -q "Up"; then
    echo "Error: postgres is not running. Run scripts/setup.sh first."
    exit 1
fi

echo "=== Seeding Database ==="

echo "[1/3] Creating admin user (admin@betfront.com / admin123) ..."
docker compose exec -T backend python -c "
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
db = SessionLocal()
try:
    existing = db.query(User).filter(User.email == 'admin@betfront.com').first()
    if existing:
        print('       Admin user already exists — skipping.')
    else:
        admin = User(
            email='admin@betfront.com',
            username='admin',
            hashed_password=get_password_hash('admin123'),
            is_active=True,
            is_superuser=True,
        )
        db.add(admin)
        db.commit()
        print('       Admin user created.')
finally:
    db.close()
"

echo "[2/3] Creating sample bankroll ..."
docker compose exec -T backend python -c "
from app.database import SessionLocal
from app.models.bankroll import Bankroll
db = SessionLocal()
try:
    existing = db.query(Bankroll).first()
    if existing:
        print('       Bankroll already exists — skipping.')
    else:
        bankroll = Bankroll(
            name='Main Bankroll',
            initial_balance=10000.00,
            current_balance=10000.00,
            currency='USD',
        )
        db.add(bankroll)
        db.commit()
        print('       Sample bankroll created (\$10,000.00).')
finally:
    db.close()
"

echo "[3/3] Running initial scrape job ..."
docker compose exec -T backend python -c "
from app.jobs.scraper import run_scrape
print('       Triggering initial scrape...')
result = run_scrape()
print(f'       Scrape result: {result}')
"

echo ""
echo "=== Seeding complete ==="
echo "  Admin login:  admin@betfront.com / admin123"
echo "  Bankroll:     \$10,000.00"
echo ""
