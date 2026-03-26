"""
Pipeline Fase 1: Ingesta y extracción.
Carga PDF → extrae texto → analiza con LLM → devuelve Markdown + JSON para el frontend.
"""
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from .extract import (
    analyze_plan_with_llm,
    extract_plan_tematico_section,
    structure_to_frontend_json,
)
from .paths import document_dir, ensure_dir, plans_dir, sanitize_folder_name
from .pdf import extract_text_from_pdf, save_document_source


def ingest_pdf(
    file_bytes: bytes,
    filename: str,
    document_id: Optional[str] = None,
    model: Optional[str] = None,
    save_source: bool = True,
    subject: Optional[str] = None,
    career: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Ejecuta la Fase 1 completa: parsing del PDF, análisis con LLM y generación de salidas.

    :param file_bytes: Contenido binario del PDF.
    :param filename: Nombre original del archivo (ej. "syllabus.pdf").
    :param document_id: ID único del documento; si no se pasa, se genera un UUID.
    :param model: Modelo LLM a usar (opcional).
    :param save_source: Si True, guarda el PDF original en disco (para auditoría/Fase 2).
    :param subject: Asignatura/materia (opcional). Si se pasa, se usa para la carpeta y para el JSON; si no, se usa lo que extraiga el LLM.
    :param career: Carrera (opcional). Si se pasa, se usa en el JSON; si no, se usa lo que extraiga el LLM.
    :return: Diccionario con:
        - document_id: str
        - raw_text: str (texto extraído del PDF)
        - raw_text_path: str (ruta del .txt con todo el texto extraído, para inspección)
        - structure: dict (JSON para el frontend)
        - markdown_path: str (ruta del .md del plan guardado)
        - source_path: str | None (ruta del PDF guardado, si save_source=True)
    """
    doc_id = document_id or str(uuid.uuid4())

    # 1. Extracción de texto
    raw_text = extract_text_from_pdf(file_bytes)
    if not raw_text.strip():
        raise ValueError("El PDF no contiene texto extraíble.")

    # 2. Análisis con LLM → estructura + markdown
    structure, markdown_content = analyze_plan_with_llm(raw_text, model=model)
    # Asignatura y carrera: prioridad a los parámetros; si no, lo que extrajo el LLM
    subject_value = (subject or (structure.get("subject") or "")).strip()
    career_value = (career or (structure.get("career") or "")).strip()
    structure["subject"] = subject_value
    structure["career"] = career_value
    subject_folder = sanitize_folder_name(subject_value) if subject_value else "sin_asignatura"

    # 3. Guardar todo en carpetas por materia: data/documents/<materia>/<doc_id>/, data/plans/<materia>/
    doc_dir = ensure_dir(document_dir(subject_folder) / doc_id)
    raw_text_path = doc_dir / "extracted.txt"
    raw_text_path.write_text(raw_text, encoding="utf-8")
    plan_section = extract_plan_tematico_section(raw_text)
    if len(plan_section) >= 100:
        (doc_dir / "plan_section.txt").write_text(plan_section, encoding="utf-8")

    source_path = None
    if save_source:
        source_path = save_document_source(
            doc_id, file_bytes, filename, base_dir=document_dir(subject_folder)
        )

    plans = plans_dir(subject_folder)
    md_name = f"{doc_id}_plan.md"
    markdown_path = plans / md_name
    # Regenerar markdown con career/subject actualizados por si se pasaron por parámetro
    from .extract import _structure_to_markdown
    markdown_path.write_text(_structure_to_markdown(structure), encoding="utf-8")

    # 4. JSON para el frontend (selectores)
    frontend_structure = structure_to_frontend_json(structure)

    return {
        "document_id": doc_id,
        "raw_text": raw_text,
        "raw_text_path": str(raw_text_path.resolve()),
        "structure": frontend_structure,
        "markdown_path": str(markdown_path.resolve()),
        "source_path": str(source_path) if source_path else None,
    }


def run_ingest_from_file(
    pdf_path: str | Path,
    document_id: Optional[str] = None,
    model: Optional[str] = None,
    subject: Optional[str] = None,
    career: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Conveniencia: ejecuta ingest_pdf leyendo el PDF desde un archivo en disco.

    :param pdf_path: Ruta al archivo .pdf.
    :param document_id: Opcional.
    :param model: Opcional.
    :param subject: Asignatura/materia (opcional). Se usa para la carpeta y el JSON.
    :param career: Carrera (opcional). Se usa en el JSON.
    :return: Mismo dict que ingest_pdf().
    """
    path = Path(pdf_path)
    if not path.exists() or not path.suffix.lower() == ".pdf":
        raise ValueError(f"Archivo PDF no encontrado o extensión incorrecta: {path}")
    file_bytes = path.read_bytes()
    return ingest_pdf(
        file_bytes,
        filename=path.name,
        document_id=document_id,
        model=model,
        save_source=True,
        subject=subject,
        career=career,
    )
