#!/bin/bash
set -e

# Configurazione
KEY_NAME="ctf_proxy_rsa_key"  # Nome della chiave
HOST_SSH_DIR="$HOME/.ssh"
HOST_AUTH_KEYS="$HOST_SSH_DIR/authorized_keys"
CONTAINER_KEY_DIR="./ssh_keys"  # Directory per il container (montata via Docker)
NETWORK_INTERFACE="game" 

# Install ip table
apt-get update
apt-get install -y iptables

# Ip locale per ricevere i pacchetti dal proxy
# Check if the address has been already added
if ! ip addr show $NETWORK_INTERFACE | grep -q "198.18.0.42/32"; then
    ip addr add 198.18.0.42/32 dev $NETWORK_INTERFACE
fi


# 1. Genera la chiave per il container (se non esiste)
mkdir -p "$CONTAINER_KEY_DIR"
if [ ! -f "$CONTAINER_KEY_DIR/$KEY_NAME" ]; then
    echo "✅ Generazione chiave SSH per il container..."
    ssh-keygen -t rsa -b 2048 -f "$CONTAINER_KEY_DIR/$KEY_NAME" -N ""  # No passphrase
    chmod 600 "$CONTAINER_KEY_DIR/$KEY_NAME"  # Permessi rigorosi per la chiave privata
else
    echo "ℹ️  Chiave esistente, salto generazione."
fi

# 2. Configura l'host per accettare la connessione SSH
mkdir -p "$HOST_SSH_DIR"
chmod 700 "$HOST_SSH_DIR"

# Aggiungi la chiave pubblica all'host (senza duplicati)
PUB_KEY=$(cat "$CONTAINER_KEY_DIR/$KEY_NAME.pub")
if ! grep -qF "$PUB_KEY" "$HOST_AUTH_KEYS" 2>/dev/null; then
    echo "➕ Aggiungo chiave pubblica all'host..."
    echo "$PUB_KEY" >> "$HOST_AUTH_KEYS"
    chmod 600 "$HOST_AUTH_KEYS"
else
    echo "🔐 Chiave pubblica già presente in authorized_keys."
fi

# 3. Avvia i container Docker
echo "🚀 Avvio dei servizi Docker..."
docker compose up -d --build