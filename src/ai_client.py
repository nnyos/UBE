import os

from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración obtenida del entorno con valores por defecto
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://172.17.0.1:11434/v1")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "mistral-nemo")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")

# Configuración del cliente para conectar con Ollama (API compatible con OpenAI)
client = OpenAI(
    base_url=OLLAMA_URL,
    api_key=OLLAMA_API_KEY,
)


def ask_local_ai(prompt, model=None):
    """
    Envía una consulta al modelo local usando la API compatible con OpenAI.
    """
    # Usar el modelo por defecto si no se especifica uno
    target_model = model or DEFAULT_MODEL

    print(f"📡 Enviando consulta a {target_model} en {OLLAMA_URL}...")

    try:
        response = client.chat.completions.create(
            model=target_model,
            messages=[
                {"role": "system", "content": "Eres un asistente útil corriendo localmente vía Ollama."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Error de conexión: {str(e)}\nTip: Asegúrate de que '{OLLAMA_URL}' sea accesible desde Docker."
