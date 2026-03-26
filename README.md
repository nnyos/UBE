# UBE (Ingesta de PDFs + extracción de “Plan Temático”)

Este proyecto automatiza la **Fase 1 (ingesta y extracción)** de PDFs tipo syllabus/plan de estudios:
1) extrae el texto del PDF,
2) consulta un LLM que corre localmente (vía **Ollama**),
3) devuelve una **estructura JSON** lista para frontend y también un **Markdown** del plan.

Los artefactos se guardan en `data/`.

## Qué incluye el proyecto

- `src/document_pipeline/`:
  - extracción de texto desde PDF (PyMuPDF),
  - pre-procesamiento para reducir ruido,
  - llamada al LLM,
  - parseo robusto de JSON,
  - generación del `.md` y el JSON para el frontend.
- `scripts/run_ingest.py`:
  - ejecuta la Fase 1 con un PDF.
- `scripts/create_sample_pdf.py`:
  - genera un PDF de ejemplo para probar el pipeline.
- `src/main.py`:
  - script simple para probar conectividad con el modelo (pregunta/ respuesta).

## Requisitos

- Python 3.10+ (este repo usa 3.11 en el devcontainer)
- Sistema:
  - Docker instalado (si vas a usar Ollama con `docker`)
  - (opcional) NVIDIA drivers + NVIDIA Container Toolkit si quieres GPU
- Un modelo disponible en Ollama (por defecto usa `DEFAULT_MODEL` del `.env`)

## 1) Instalar dependencias

```bash
cd /workspaces/ube
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Configurar Ollama (recomendado con Docker)

### Opción A: Docker Compose

```bash
docker compose up -d
```

`compose.yml` expone Ollama en `http://localhost:11434`.

> Nota: la sección `deploy` de GPUs en `compose.yml` puede depender de tu configuración de Docker Compose (en algunos entornos solo aplica en modo swarm). Si necesitas asegurarte de GPU, usa la Opción B.

### Opción B: Script para Ollama (GPU con `--gpus all`)

```bash
./exec/run-ollama.sh llama3
```

Este script:
- levanta un contenedor llamado `ollama-gpu`,
- publica `11434:11434`,
- hace `ollama pull` del modelo que le pases.

Si no tienes GPU configurada para Docker, ejecuta (opcional, requiere `sudo`):

```bash
sudo ./exec/configurar-docker-nvidia.sh
```

## 3) Configurar variables de entorno (`.env`)

El código carga variables desde `.env` usando `python-dotenv`.

Copia el ejemplo:

```bash
cp .env.example.local .env
```

Asegúrate de que `OLLAMA_URL` apunte a donde corre tu Ollama:
- si usas Docker y el puerto publicado es `11434`, usa:
  - `OLLAMA_URL=http://localhost:11434/v1`

Importante: en este repo el `.env.example.local` trae un puerto `12434`, pero los scripts/compose exponen `11434`. Ajusta `OLLAMA_URL` para que coincida con tu Ollama real.

## 4) Probar el pipeline con el PDF de ejemplo

Primero, crea el PDF de muestra:

```bash
python scripts/create_sample_pdf.py
```

Luego ejecuta la ingestión:

```bash
python scripts/run_ingest.py data/sample_plan.pdf
```

O si el archivo existe, puedes omitir la ruta:

```bash
python scripts/run_ingest.py
```

Al terminar verás algo como:
- `document_id`
- `raw_text_path`
- `markdown_path`
- `source_path` (si guardas la fuente)

## 5) Dónde se guardan los resultados

Por materia/asignatura:
- PDFs y texto extraído:
  - `data/documents/<materia>/<document_id>/extracted.txt`
  - `data/documents/<materia>/<document_id>/<original.pdf>` (si `save_source=True`)
- Markdown del plan:
  - `data/plans/<materia>/<document_id>_plan.md`

También devuelve en consola el `structure` (JSON) para “frontend selectors”.

## Uso como librería (desde Python)

```python
from document_pipeline import run_ingest_from_file

result = run_ingest_from_file("ruta/al/syllabus.pdf", subject="Programación", career="Ingeniería")
structure = result["structure"]          # JSON para frontend
markdown_path = result["markdown_path"]  # ruta al .md generado
```

## Consideraciones sobre prompts

`src/document_pipeline/extract.py` intenta leer un prompt de sistema desde:
- `prompts/plan_extract_system.txt`

Si ese archivo no existe, se usa un prompt fallback embebido en el código (igual funciona, pero puedes mejorar la calidad creando el archivo).

## Solución de problemas rápida

- “Error de conexión / no encuentra Ollama”:
  - revisa `OLLAMA_URL` (puerto y host),
  - verifica que Ollama esté arriba (`docker compose ps` o el script `run-ollama.sh`).
- “No genera texto útil desde el PDF”:
  - algunos PDFs son escaneados (imagen) y no traen texto embebido; este pipeline usa extracción de texto estándar.

