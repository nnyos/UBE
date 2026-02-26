import sys

from ai_client import ask_local_ai

if __name__ == "__main__":
    # Uso: python src/main.py "Hola, ¿qué tal?" [modelo]
    user_prompt = sys.argv[1] if len(
        sys.argv) > 1 else "Preséntate brevemente y confirma que eres Llama 3."
    target_model = sys.argv[2] if len(sys.argv) > 2 else "llama3"

    result = ask_local_ai(user_prompt, target_model)

    print("\n--- Respuesta ---")
    print(result)
    print("-----------------\n")
