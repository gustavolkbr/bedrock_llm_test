"""
Configuração do modelo juiz — mesmo padrão do mês 1 (demos/juiz.py),
com um branch novo para usar um modelo do Bedrock como juiz.

Variáveis de ambiente:
    JUIZ_PROVIDER   bedrock (padrão) | ollama | gemini
    JUIZ_MODEL      nome do modelo juiz
    AWS_REGION      região do Bedrock (padrão: us-east-2)
    OLLAMA_URL      URL do Ollama (só se JUIZ_PROVIDER=ollama)
    GEMINI_API_KEY  chave do Google AI Studio (só se JUIZ_PROVIDER=gemini)

Por que Bedrock como juiz padrão neste desafio: o bot testado (Haiku) já
roda na AWS; usar um modelo Bedrock mais forte (Sonnet) como juiz mantém
a regra de "juiz deve ser mais capaz que o modelo avaliado" sem depender
de uma chave de API externa nova.
"""
import os


def obter_juiz():
    provider = os.getenv("JUIZ_PROVIDER", "bedrock").lower()

    if provider == "bedrock":
        from deepeval.models import AmazonBedrockModel  # requer: pip install aiobotocore botocore

        return AmazonBedrockModel(
            model=os.getenv("JUIZ_MODEL", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"),
            region=os.getenv("AWS_REGION", "us-east-2"),
            generation_kwargs={"temperature": 0},
        )

    if provider == "gemini":
        from deepeval.models import GeminiModel  # requer: pip install google-genai

        return GeminiModel(
            model=os.getenv("JUIZ_MODEL", "gemini-2.0-flash"),
            api_key=os.getenv("GEMINI_API_KEY"),
        )

    from deepeval.models import OllamaModel  # requer: pip install ollama

    return OllamaModel(
        model=os.getenv("JUIZ_MODEL", "llama3.2:3b"),
        base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
    )
