"""
Extracción de texto desde PDF y almacenamiento del archivo fuente (Fase 1).
"""
from pathlib import Path

import fitz

from .paths import document_dir, ensure_dir


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extrae el texto crudo de un PDF usando PyMuPDF.

    :param file_bytes: Contenido binario del PDF.
    :return: Texto plano extraído (todas las páginas concatenadas).
    :raises ValueError: Si los bytes no corresponden a un PDF válido.
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        try:
            parts = []
            for page in doc:
                parts.append(page.get_text())
            return "\n".join(parts).strip()
        finally:
            doc.close()
    except Exception as e:
        raise ValueError(f"Error al extraer texto del PDF: {e}") from e


def save_document_source(
    document_id: str,
    file_bytes: bytes,
    filename: str,
    base_dir: Path | None = None,
) -> Path:
    """
    Guarda el PDF original asociado a un document_id.
    Útil para auditoría y reutilización (Fase 2).

    :param document_id: Identificador único del documento (ej. UUID).
    :param file_bytes: Contenido binario del PDF.
    :param filename: Nombre original del archivo (ej. "syllabus.pdf").
    :param base_dir: Si se pasa, se usa esta carpeta en lugar de document_dir() (ej. por materia).
    :return: Ruta absoluta del archivo guardado.
    """
    base = base_dir if base_dir is not None else document_dir()
    # Subcarpeta por document_id para no colisionar
    subdir = ensure_dir(base / document_id)
    # Conservar extensión; si no hay, usar .pdf
    name = Path(filename).name
    if not name.lower().endswith(".pdf"):
        name = f"{name}.pdf"
    path = subdir / name
    path.write_bytes(file_bytes)
    return path.resolve()
