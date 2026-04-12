#!/bin/bash
# Deployment script for Project Phoenix
# Run on the server after git pull

set -e

echo "=== Project Phoenix Deploy ==="

# 1. Install/update Python dependencies
echo "[1/6] Installing Python dependencies..."
uv sync --no-dev

# 2. Install/update Node dependencies and build CSS
echo "[2/6] Building Tailwind CSS..."
npm ci --production=false
npm run build

# 3. Run database migrations
echo "[3/6] Running database migrations..."
uv run alembic upgrade head

# 4. Collect static files (if using external storage)
echo "[4/6] Static files ready."

# 5. Restart services
echo "[5/6] Restarting services..."
sudo systemctl restart phoenix-web
sudo systemctl restart phoenix-worker
sudo systemctl restart phoenix-beat

# 6. Verify
echo "[6/6] Verifying..."
sleep 2
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ | grep -q "200" && echo "Web: OK" || echo "Web: FAILED"

echo "=== Deploy complete ==="
