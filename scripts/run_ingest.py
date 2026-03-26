"""
Prueba el pipeline de ingesta (Fase 1) con un PDF.

Uso:
  # Con tu propio PDF:
  PYTHONPATH=src python scripts/run_ingest.py /ruta/a/syllabus.pdf

  # Con el PDF de ejemplo (primero créalo):
  PYTHONPATH=src python scripts/create_sample_pdf.py
  PYTHONPATH=src python scripts/run_ingest.py data/sample_plan.pdf
"""
import json
import sys
from pathlib import Path

# Raíz del proyecto y src en path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from document_pipeline import run_ingest_from_file  # noqa: E402


def main():
    if len(sys.argv) < 2:
        pdf_path = ROOT / "data" / "sample_plan.pdf"
        if not pdf_path.exists():
            print("Uso: PYTHONPATH=src python scripts/run_ingest.py <ruta_al.pdf>")
            print("O crea antes el PDF de ejemplo:")
            print("  PYTHONPATH=src python scripts/create_sample_pdf.py")
            sys.exit(1)
    else:
        pdf_path = Path(sys.argv[1])

    print(f"Procesando: {pdf_path}")
    print("---")

    result = run_ingest_from_file(pdf_path)

    print(f"document_id: {result['document_id']}")
    print(f"raw_text_path: {result['raw_text_path']}")
    print(f"markdown_path: {result['markdown_path']}")
    print(f"source_path: {result['source_path']}")
    print()
    print("Estructura (JSON para frontend):")
    print(json.dumps(result["structure"], indent=2, ensure_ascii=False))
    print()
    print("Contenido del plan (.md):")
    print(Path(result["markdown_path"]).read_text(encoding="utf-8")[:800])
    if len(Path(result["markdown_path"]).read_text(encoding="utf-8")) > 800:
        print("...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
