#!/usr/bin/env bash
set -euo pipefail

# Gå til projektmappen
cd "$(dirname "$0")"

# Installer Ubuntu-afhængigheder
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip mininet openvswitch-switch libpcap-dev

# Opret virtuelt Python-miljø
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi

# Installer Python-afhængigheder
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

echo "Setup complete!"