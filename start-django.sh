#!/bin/bash
# Django Server Starter Script

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Starting Django Server..."
echo "========================================"
echo ""
echo "Django API will be available at:"
echo "  http://localhost:9000"
echo ""
echo "Django Admin:"
echo "  http://localhost:9000/admin"
echo ""
echo "Database: SQLite by default (set DB_ENGINE=mysql for MySQL)"
echo ""
echo "========================================"
echo "Press Ctrl+C to stop the server"
echo ""

cd "$DIR"

if [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
else
  echo "ERROR: Virtual environment not found. Run: python -m venv venv"
  exit 1
fi

python manage.py runserver 0.0.0.0:9000
