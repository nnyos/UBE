#!/bin/bash
# ==============================================================================
# Script: configurar-docker-nvidia.sh
# Descripción: Configura NVIDIA Container Toolkit para Docker en Ubuntu 24.04+
# ==============================================================================
set -euo pipefail

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo "🚀 Iniciando configuración de Docker + GPU (NVIDIA Container Toolkit)..."

# 1. Validaciones iniciales
echo ""
if [[ $EUID -ne 0 ]]; then
   error "Este script debe ejecutarse con sudo o como root."
fi

if ! command -v docker &> /dev/null; then
    error "Docker no está instalado. Instálalo primero (e.g., sudo apt install docker.io)"
fi

if ! command -v nvidia-smi &> /dev/null; then
    warn "No se detectó 'nvidia-smi'. Asegúrate de tener instalados los drivers de NVIDIA en el host."
    read -p "¿Deseas continuar de todas formas? (s/n): " confirm
    [[ $confirm != [sS] ]] && exit 1
fi

# 2. Configurar el repositorio oficial de NVIDIA
echo ""
log "🛠️ Configurando el repositorio de NVIDIA Container Toolkit..."

KEYRING_PATH="/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg"
LIST_PATH="/etc/apt/sources.list.d/nvidia-container-toolkit.list"

curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
    gpg --dearmor -o "$KEYRING_PATH" --yes

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed "s#deb https://#deb [signed-by=$KEYRING_PATH] https://#g" | \
    tee "$LIST_PATH" > /dev/null

# 3. Actualizar e Instalar
echo ""
log "🔄 Actualizando repositorios e instalando el toolkit..."
apt-get update -qq
apt-get install -y nvidia-container-toolkit

# 4. Configurar el Runtime de Docker
echo ""
log "⚙️ Configurando el motor de Docker para usar el runtime de NVIDIA..."
nvidia-ctk runtime configure --runtime=docker

echo ""
log "🔄 Reiniciando el servicio de Docker..."
systemctl restart docker

# 5. Asegurar el contexto nativo
echo ""
log "🌐 Asegurando contexto 'default' de Docker..."
docker context use default || warn "No se pudo cambiar al contexto 'default', procediendo con el actual."

# 6. Prueba Final
echo ""
log "🔍 Verificando acceso a GPU desde un contenedor..."
TEST_IMAGE="nvidia/cuda:12.4.1-base-ubuntu22.04"

if docker run --rm --gpus all "$TEST_IMAGE" nvidia-smi; then
    echo ""
    log "✅ ¡Configuración completada con éxito!"
else
    echo ""
    error "❌ La prueba de GPU falló. Revisa los logs de Docker y los drivers de NVIDIA."
fi
