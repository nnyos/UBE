import os
import re
import sys

from ai_client import ask_local_ai


def slugify(text):
    """
    Limpia un texto para usarlo como nombre de carpeta o archivo.
    """
    text = text.lower().strip()
    # Limpieza de tildes
    text = re.sub(r'[áéíóúñ]', lambda m: {
                  'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n'}[m.group()], text)
    # Solo alfanuméricos y espacios
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.replace(' ', '_')[:50]


def load_prompt_template(filename, **kwargs):
    """
    Lee un archivo de plantilla y reemplaza los marcadores {key} con los valores pasados.
    """
    path = os.path.join("prompts", filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            template = f.read()
        return template.format(**kwargs)
    except Exception as e:
        print(f"❌ Error al cargar la plantilla {filename}: {str(e)}")
        return None


def save_content_to_path(career, subject, unit, content, doc_type):
    """
    Guarda el contenido en la ruta: output/carrera/materia/unidad/tipo_unidad.md
    """
    root_output = "output"
    base_path = os.path.join(root_output, slugify(
        career), slugify(subject), slugify(unit))

    try:
        os.makedirs(base_path, exist_ok=True)
        filename = f"{doc_type}_{slugify(unit)}.md"
        full_path = os.path.join(base_path, filename)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        return full_path
    except Exception as e:
        print(f"❌ Error al guardar {doc_type}: {str(e)}")
        return None


def main():
    if len(sys.argv) < 4:
        print("Uso: python src/generate_task.py 'Carrera' 'Materia' 'Unidad' 'Contenido'")
        return

    # Parámetros básicos
    context = {
        "career": sys.argv[1],
        "subject": sys.argv[2],
        "unit": sys.argv[3],
        "raw_input": sys.argv[4] if len(sys.argv) > 4 else sys.argv[3]
    }

    print(
        f"📂 Iniciando proceso para {context['career']} > {context['subject']} > {context['unit']}")

    # 1. Cargar y generar TALLER
    prompt_taller = load_prompt_template("taller_template.md", **context)
    if prompt_taller:
        print("🚀 Generando TALLER desde plantilla...")
        res_taller = ask_local_ai(prompt_taller)
        if "❌ Error" not in res_taller:
            p = save_content_to_path(
                context["career"], context["subject"], context["unit"], res_taller, "taller")
            print(f"✅ Taller guardado en: {p}")

    # 2. Cargar y generar TAREA
    prompt_tarea = load_prompt_template("tarea_template.md", **context)
    if prompt_tarea:
        print("🚀 Generando TAREA desde plantilla...")
        res_tarea = ask_local_ai(prompt_tarea)
        if "❌ Error" not in res_tarea:
            p = save_content_to_path(
                context["career"], context["subject"], context["unit"], res_tarea, "tarea")
            print(f"✅ Tarea guardada en: {p}")


if __name__ == "__main__":
    main()
