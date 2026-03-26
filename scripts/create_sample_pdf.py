"""
Genera un PDF de ejemplo con texto de plan de estudios para probar el pipeline.
Uso: PYTHONPATH=src python scripts/create_sample_pdf.py [ruta_salida]
"""
import sys
from pathlib import Path

# Permitir importar desde src
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import fitz

PLAN_TEXT = """
PLAN DE ESTUDIOS - INGENIERÍA EN SISTEMAS
Asignatura: Programación II

UNIDAD 1: Estructuras de datos básicas
Tema 1.1: Listas y arrays
- Resultado: Implementar programas que usen listas y arrays para almacenar datos.
- Resultado: Explicar la complejidad de las operaciones de inserción y búsqueda.

Tema 1.2: Pilas y colas
- Resultado: Implementar una pila y una cola en el lenguaje de programación del curso.
- Resultado: Identificar problemas donde convenga usar pila o cola.

UNIDAD 2: Algoritmos de ordenamiento
Tema 2.1: Ordenamiento por comparación
- Resultado: Implementar al menos dos algoritmos de ordenamiento (burbuja, inserción, selección).
- Resultado: Comparar tiempos de ejecución en casos mejor y peor.

Tema 2.2: Búsqueda
- Resultado: Implementar búsqueda lineal y binaria.
- Resultado: Justificar cuándo usar cada una según el contexto.
"""


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/sample_plan.pdf")
    out.parent.mkdir(parents=True, exist_ok=True)

    doc = fitz.open()
    page = doc.new_page()
    rect_title = fitz.Rect(50, 50, 400, 90)
    page.insert_textbox(rect_title, "Plan de estudios (muestra)", fontsize=16)
    rect_body = fitz.Rect(50, 100, 550, 750)
    page.insert_textbox(rect_body, PLAN_TEXT.strip(), fontsize=11)
    doc.save(str(out))
    doc.close()

    print(f"PDF de ejemplo creado: {out.resolve()}")
    return str(out.resolve())


if __name__ == "__main__":
    main()
