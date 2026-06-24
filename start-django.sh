#!/bin/bash
# Django Server Starter Script

# Get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🚀 Starting Django Server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Django API will be available at:"
echo "   👉 http://localhost:8000"
echo ""
echo "🔐 Django Admin (create superuser first):"
echo "   👉 http://localhost:8000/admin"
echo ""
echo "🗄️  Database: MySQL (slpa_container_detection)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Press Ctrl+C to stop the server"
echo ""

# Change to project directory
cd "$DIR"

# Activate virtual environment and run server
source .venv/bin/activate
python manage.py runserver
