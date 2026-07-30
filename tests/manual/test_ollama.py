from app.services.ollama_service import OllamaService

ollama = OllamaService()

print("=" * 60)

print("Health:")

print(ollama.health_check())

print("=" * 60)

print("Modelos:")

print(ollama.list_models())

print("=" * 60)

print("Resposta:")

print(
    ollama.generate(
        "Responda apenas com a palavra: funcionando."
    )
)
