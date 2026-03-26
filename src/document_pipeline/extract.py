"""
Análisis con LLM del texto extraído: Unidades, Objetivos específicos y Contenidos por unidad (Fase 1).
Salida: objeto JSON para el frontend y contenido Markdown del plan.
"""
import json
import re
from pathlib import Path
from typing import Any, Dict

from ai_client import ask_local_ai

PROMPT_PATH = Path(__file__).resolve(
).parents[2] / "prompts" / "plan_extract_system.txt"

# Patrones de ruido típicos en PDFs de syllabus (encabezados/pies de página).
# Importante: evitar nombres de asignaturas concretas; usar sólo patrones genéricos.
NOISE_LINE_PATTERNS = re.compile(
    r"^(?:"
    r"S\s+Y\s+L\s+L\s+A\s+B\s+U\s+S|"     # SYLLABUS en columnas
    r"CÓDIGO:\s*\d*|VERSIÓN:\s*|PÁGINA:\s*\d+|"  # metadatos
    r"ACD|APE|AA|TOT\.?|"                # cabecera de columnas de horas
    r"AC\s*$|AP\s*$|E\s*$|AA\s+TOT\.?\s*$|"      # otras variantes de columnas
    r"\d{1,3}\s*$"                       # líneas que son solo un número
    r")$",
    re.IGNORECASE,
)


def extract_plan_tematico_section(raw_text: str) -> str:
    """
    Extrae solo la sección "Plan temático" del texto crudo y reduce ruido de encabezados/pies.
    Así el LLM recibe un bloque más limpio y con más espacio útil para unidades/contenidos.
    """
    text = raw_text
    # Inicio preferido: "1. PLAN TEMÁTICO" o "PLAN TEMÁTICO DE LA ASIGNATURA"
    start_m = re.search(
        r"1\.\s*PLAN\s+TEM[ÁA]TICO|PLAN\s+TEM[ÁA]TICO\s+DE\s+LA\s+ASIGNATURA",
        text,
        re.IGNORECASE,
    )
    # Fallback: tabla de UNIDADES / OBJETIVOS / CONTENIDOS, típica en muchos syllabus
    if not start_m:
        start_m = re.search(
            r"\bUNIDADES\b[\s\S]{0,80}OBJETIVOS\s+ESPEC[IÍ]FICOS[\s\S]{0,80}CONTENIDOS\s+DE\s+CADA\s+UNIDAD",
            text,
            re.IGNORECASE,
        )
    if start_m:
        text = text[start_m.start():]
    # Fin: "TOTAL HORAS" o "7. ESTRATEGIAS" (siguiente sección del syllabus)
    end_m = re.search(
        r"\n\s*TOTAL\s+HORAS\s*\n|\n\s*7\.\s*ESTRATEGIAS",
        text,
        re.IGNORECASE,
    )
    if end_m:
        text = text[: end_m.start()]

    # Quitar bloques repetidos de encabezado/pie (encabezados de página, tablas de horas, etc.)
    lines = text.splitlines()
    # Contar frecuencia de cada línea (encabezados suelen repetirse en cada página)
    freq: dict[str, int] = {}
    for line in lines:
        s = line.strip()
        if not s:
            continue
        freq[s] = freq.get(s, 0) + 1

    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned.append("")
            continue
        # Patrones genéricos conocidos (SYLLABUS, CÓDIGO, PÁGINA, columnas de horas, números sueltos)
        if NOISE_LINE_PATTERNS.match(stripped):
            continue
        # Encabezados muy repetidos, en mayúsculas y cortos (suelen ser nombres de asignatura o secciones)
        if (
            freq.get(stripped, 0) >= 2
            and len(stripped) <= 40
            and stripped.upper() == stripped
        ):
            continue
        cleaned.append(line)
    # Reducir líneas en blanco consecutivas a máximo 2
    normalized = re.sub(r"\n{3,}", "\n\n", "\n".join(cleaned))
    return normalized.strip()


def _load_system_prompt() -> str:
    """Carga el prompt de sistema para extracción de estructura."""
    if not PROMPT_PATH.exists():
        return (
            "Responde ÚNICAMENTE con un JSON válido que tenga: "
            '"career", "subject", "units". Cada unidad debe tener "id", "title", '
            '"specific_objectives" (lista de {id, description}), "contents" (lista de {id, description}).'
        )
    return PROMPT_PATH.read_text(encoding="utf-8").strip()


def _repair_truncated_json(text: str) -> str:
    """
    Intenta reparar JSON truncado (respuesta del modelo cortada a mitad de cadena).
    Cierra la cadena abierta y añade los ] } en el orden correcto (según pila de aperturas).
    """
    stripped = text.rstrip()
    if stripped.endswith(","):
        stripped = stripped[:-1]
    # Cerrar cadena truncada
    if not stripped.endswith(("}", "]", '"')):
        stripped += '"'
    # Construir secuencia de cierre en orden correcto: recorrer y apilar [ {
    stack = []
    i = 0
    in_string = False
    escape = False
    quote_char = None
    while i < len(stripped):
        c = stripped[i]
        if in_string:
            if escape:
                escape = False
            elif c == "\\" and quote_char == '"':
                escape = True
            elif c == quote_char:
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
            quote_char = c
        elif c == "{":
            stack.append("}")
        elif c == "[":
            stack.append("]")
        elif c in "}]" and stack:
            stack.pop()
        i += 1
    stripped += "".join(reversed(stack))
    return stripped


def _parse_json_from_llm(response: str) -> Dict[str, Any]:
    """Extrae y parsea JSON de la respuesta del LLM (puede venir envuelta en ```json ... ```)."""
    text = response.strip()
    # Quitar bloque markdown de código
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        if "Unterminated string" in str(e) or "Expecting" in str(e):
            try:
                repaired = _repair_truncated_json(text)
                return json.loads(repaired)
            except json.JSONDecodeError:
                pass
        raise


def _structure_to_markdown(structure: Dict[str, Any]) -> str:
    """Genera el contenido Markdown del plan con formato claro: Unidades numeradas, objetivos y contenidos."""
    career = structure.get("career", "N/A")
    subject = structure.get("subject", "N/A")
    units = structure.get("units", [])

    lines = [
        "# Plan temático de la asignatura",
        "",
        "| | |",
        "|---|---|",
        f"| **Carrera** | {career} |",
        f"| **Asignatura** | {subject} |",
        "",
        "---",
        "",
    ]

    for i, unit in enumerate(units, 1):
        title = unit.get("title", "Sin título")
        lines.append(f"## {i}. {title}")
        lines.append("")

        objectives = unit.get("specific_objectives", [])
        if objectives:
            lines.append("### Objetivos específicos")
            lines.append("")
            for obj in objectives:
                desc = obj.get("description", "").strip()
                if desc:
                    lines.append(f"- {desc}")
            lines.append("")

        contents = unit.get("contents", [])
        if contents:
            lines.append("### Contenidos")
            lines.append("")
            for cont in contents:
                desc = cont.get("description", "").strip()
                if desc:
                    lines.append(f"- {desc}")
            lines.append("")

    return "\n".join(lines).rstrip()


def _analyze_text_block_with_llm(
    text_block: str,
    model: str | None = None,
    single_unit_hint: bool = False,
) -> Dict[str, Any]:
    """
    Envía un bloque de texto (una o varias unidades) al LLM y devuelve
    sólo la estructura JSON parseada.
    """
    # Limitar tamaño para no superar contexto del modelo; este helper supone
    # que text_block ya es la sección de plan temático (o parte de ella).
    max_chars = 15000
    truncated = text_block[:max_chars]
    system = _load_system_prompt()
    intro = (
        "El siguiente texto corresponde a UNA sola unidad (objetivos y contenidos). "
        "Extrae esa unidad completa con TODOS los objetivos y TODOS los contenidos (ítems con -, ●, o).\n\n---\n"
        if single_unit_hint
        else "Analiza el siguiente plan temático (solo la sección de unidades/objetivos/contenidos) y extrae la estructura en JSON.\n\n---\n"
    )
    user = f"{intro}{truncated}"
    if len(text_block) > max_chars:
        user += "\n\n[... texto truncado por límite de contexto ...]"

    response = ask_local_ai(user, model=model, system=system)

    if response.startswith("❌"):
        raise ValueError(response)

    try:
        return _parse_json_from_llm(response)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"La respuesta del modelo no es un JSON válido: {e}") from e


def analyze_plan_with_llm(
    raw_text: str,
    model: str | None = None,
) -> tuple[Dict[str, Any], str]:
    """
    Envía el texto del plan al LLM y obtiene la estructura (JSON) y el Markdown.

    Estrategia robusta para sílabos largos:
    - 1ª llamada: analiza todo el plan temático.
    - Si hay varias unidades, se lanza una 2ª llamada sólo con el texto
      de la última unidad, y se reemplaza esa unidad en la estructura
      inicial. Así evitamos truncados en la última unidad por límite de
      contexto del modelo.
    """
    # Preprocesar: extraer solo la sección Plan temático y quitar ruido (encabezados/pies)
    text_for_llm = extract_plan_tematico_section(raw_text)
    if len(text_for_llm) < 500:
        text_for_llm = raw_text  # Si no se encontró sección, usar todo

    # 1) Llamada principal: todas las unidades
    structure = _analyze_text_block_with_llm(text_for_llm, model=model)
    if "units" not in structure:
        structure["units"] = []

    units = structure.get("units", [])

    # 2) Refinar la última unidad con una llamada enfocada, para evitar truncados
    if units:
        last_title = (units[-1].get("title") or "").strip()
        if last_title:
            # Buscar el título en el texto (puede estar en varias líneas en el PDF)
            # Construir regex: "Gestión y Optimización..." -> Gestión\s+y\s+Optimización...
            title_pattern = r"\s+".join(re.escape(w) for w in last_title.split())
            title_re = re.compile(title_pattern, re.IGNORECASE)
            matches = list(title_re.finditer(text_for_llm))
            # Primera ocurrencia: suele ser encabezado de contenidos de la última unidad; así el tail incluye todos los contenidos
            idx = matches[0].start() if matches else -1
            if idx != -1:
                tail_text = text_for_llm[idx:]
                try:
                    tail_structure = _analyze_text_block_with_llm(
                        tail_text,
                        model=model,
                        single_unit_hint=True,
                    )
                    tail_units = tail_structure.get("units", [])
                    if tail_units:
                        # Reemplazar la última unidad con la analizada en la 2ª pasada
                        structure["units"] = units[:-1] + [tail_units[0]]
                except Exception:
                    # Si falla la llamada de refinado, dejamos la estructura original.
                    pass

    markdown_content = _structure_to_markdown(structure)
    return structure, markdown_content


def structure_to_frontend_json(structure: Dict[str, Any]) -> Dict[str, Any]:
    """
    Devuelve el mismo objeto de estructura listo para enviar al frontend:
    Unidades, con objetivos específicos y contenidos de cada unidad.
    """
    return {
        "career": structure.get("career", ""),
        "subject": structure.get("subject", ""),
        "units": [
            {
                "id": u.get("id", ""),
                "title": u.get("title", ""),
                "specific_objectives": [
                    {"id": o.get("id", ""), "description": o.get(
                        "description", "")}
                    for o in u.get("specific_objectives", [])
                ],
                "contents": [
                    {"id": c.get("id", ""), "description": c.get(
                        "description", "")}
                    for c in u.get("contents", [])
                ],
            }
            for u in structure.get("units", [])
        ],
    }
