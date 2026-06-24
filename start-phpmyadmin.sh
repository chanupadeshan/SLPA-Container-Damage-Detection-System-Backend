#!/bin/bash
# phpMyAdmin Starter Script

echo "🚀 Starting phpMyAdmin..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 phpMyAdmin will be available at:"
echo "   👉 http://localhost:8080"
echo ""
echo "🔐 Login Credentials:"
echo "   Server: (leave empty or type 'localhost')"
echo "   Username: root"
echo "   Password: (leave empty, just click 'Go')"
echo ""
echo "🗄️  Database Name: slpa_container_detection"
echo ""
echo "✅ Password-less login is now enabled!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Press Ctrl+C to stop phpMyAdmin"
echo ""

# Start PHP built-in server
php -S localhost:8080 -t /opt/homebrew/share/phpmyadmin
