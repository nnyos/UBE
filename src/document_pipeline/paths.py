"""
Rutas y directorios para el pipeline de documentos (Fase 1).
"""
import os
import re
from pathlib import Path

# Raíz del proyecto (donde está compose.yml / README)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
# Directorio de datos: PDFs, markdown y artefactos
DATA_DIR = Path(os.getenv("UBE_DATA_DIR", str(PROJECT_ROOT / "data")))
DOCUMENTS_DIR = DATA_DIR / "documents"
PLANS_DIR = DATA_DIR / "plans"  # Markdown de planes extraídos


def ensure_dir(path: Path) -> Path:
    """Crea el directorio (y padres) si no existe. Devuelve el path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def sanitize_folder_name(name: str, max_len: int = 80) -> str:
    """
    Convierte el nombre de la materia/asignatura en un nombre de carpeta seguro.
    Elimina caracteres no válidos y limita la longitud.
    """
    if not name or not name.strip():
        return "sin_asignatura"
    # Minúsculas, reemplazar espacios y caracteres problemáticos por _
    s = re.sub(r"[^\w\s\-]", "", name.strip(), flags=re.UNICODE)
    s = re.sub(r"[\s\-]+", "_", s).strip("_")
    s = s or "sin_asignatura"
    return s[:max_len] if len(s) > max_len else s


def document_dir(subject: str | None = None) -> Path:
    """
    Directorio donde se guardan los PDFs y textos extraídos.
    Si se pasa subject (materia/asignatura), devuelve documents/<subject>/.
    """
    if subject:
        return ensure_dir(DOCUMENTS_DIR / sanitize_folder_name(subject))
    return ensure_dir(DOCUMENTS_DIR)


def plans_dir(subject: str | None = None) -> Path:
    """
    Directorio donde se guardan los .md con la estructura del plan.
    Si se pasa subject (materia/asignatura), devuelve plans/<subject>/.
    """
    if subject:
        return ensure_dir(PLANS_DIR / sanitize_folder_name(subject))
    return ensure_dir(PLANS_DIR)
