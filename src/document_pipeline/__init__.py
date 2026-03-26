"""
Pipeline de documentos — Fase 1: Ingesta y extracción.

Uso desde backend (ej. POST de PDF):

    from document_pipeline import ingest_pdf

    result = ingest_pdf(file_bytes, filename="syllabus.pdf")
    # result["structure"] → JSON para selectores (Unidad / Tema / Resultado)
    # result["markdown_path"] → ruta del .md del plan
"""

from .extract import analyze_plan_with_llm, structure_to_frontend_json
from .ingest import ingest_pdf, run_ingest_from_file
from .paths import document_dir, ensure_dir, plans_dir
from .pdf import extract_text_from_pdf, save_document_source

__all__ = [
    "ingest_pdf",
    "run_ingest_from_file",
    "extract_text_from_pdf",
    "save_document_source",
    "analyze_plan_with_llm",
    "structure_to_frontend_json",
    "document_dir",
    "plans_dir",
    "ensure_dir",
]
