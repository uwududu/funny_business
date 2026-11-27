#!/bin/bash

Script de instalação para Ubuntu


set -e # Interrompe a execução em caso de erro em qualquer comando

echo "=== Atualizando repositórios e pacotes ==="

echo "=== Instalando dependências básicas (curl, flatpak, snap, python3) ==="
sudo apt install -y python3 python3-pip 

echo "=== Instalação concluída com sucesso! ==="