#!/bin/bash
# Setup SSL per banddecoder con nginx come reverse proxy
# Sposta Flask su 127.0.0.1:5001, nginx espone HTTPS su :5000

set -e

CERT_DIR="/etc/ssl/banddecoder"
NGINX_CONF="/etc/nginx/sites-available/banddecoder"
DOMAIN="io7t.ddns.net"

echo "=== Installazione nginx ==="
sudo apt-get install -y nginx

echo "=== Generazione certificato self-signed ==="
sudo mkdir -p "$CERT_DIR"
sudo openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
    -keyout "$CERT_DIR/key.pem" \
    -out "$CERT_DIR/cert.pem" \
    -subj "/CN=$DOMAIN/O=IO7T Ham Radio/C=IT" \
    -addext "subjectAltName=DNS:$DOMAIN"

sudo chmod 600 "$CERT_DIR/key.pem"
sudo chmod 644 "$CERT_DIR/cert.pem"

echo "=== Configurazione nginx ==="
sudo cp "$(dirname "$0")/banddecoder-nginx.conf" "$NGINX_CONF"
sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/banddecoder
sudo rm -f /etc/nginx/sites-enabled/default

sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx

echo "=== Riavvio servizi banddecoder ==="
# Ferma Flask prima (potrebbe essere ancora sulla 5000), poi avvia nginx, poi Flask su 5001
sudo systemctl stop banddecoder-web 2>/dev/null || true
sudo systemctl enable nginx
sudo systemctl restart nginx
sudo systemctl reset-failed banddecoder-web 2>/dev/null || true
sudo systemctl restart banddecoder banddecoder-web

echo ""
echo "=== SSL configurato ==="
echo "Web interface: https://$DOMAIN:5000"
echo "Certificato valido fino a: $(sudo openssl x509 -enddate -noout -in $CERT_DIR/cert.pem)"
