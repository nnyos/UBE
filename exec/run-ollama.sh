#!/bin/bash
# ==============================================================================
# Script: run-ollama.sh
# Descripción: Levanta Ollama con soporte GPU y carga un modelo específico.
# Uso: ./exec/run-ollama.sh [nombre_del_modelo]
# ==============================================================================
set -euo pipefail

# Colores para la salida
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
info() { echo -e "${CYAN}[OLLAMA]${NC} $1"; }

# 1. Parámetros
MODELO=${1:-"llama3"}
CONTAINER_NAME="ollama-gpu"

echo "🦙 Iniciando Ollama con soporte para GPU..."
echo ""

# 2. Verificar si el contenedor ya existe y está corriendo
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    log "El contenedor '$CONTAINER_NAME' ya está en ejecución."
else
    if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
        log "Reiniciando contenedor existente..."
        docker start $CONTAINER_NAME > /dev/null
    else
        log "Creando nuevo contenedor Ollama con GPU..."
        docker run -d \
            --gpus all \
            -v ollama_data:/root/.ollama \
            -p 11434:11434 \
            --name "$CONTAINER_NAME" \
            ollama/ollama:latest > /dev/null
    fi
fi

# 3. Descargar/Ejecutar el modelo
echo ""
info "Asegurando que el modelo '$MODELO' esté disponible..."
docker exec -it "$CONTAINER_NAME" ollama pull "$MODELO"

echo ""
log "✅ Ollama está listo y el modelo '$MODELO' cargado."
log "Puedes interactuar con él usando: docker exec -it $CONTAINER_NAME ollama run $MODELO"
log "O mediante la API en: http://localhost:11434"
echo ""
