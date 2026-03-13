from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from src.config.settings import settings

def get_chat_model(provider: str, model_name: str, api_key: str = None):
    """
    Initializes and returns the appropriate Chat LLM model based on provider and model.
    Pass `api_key` to override the default environment variable key.
    """
    if provider == "Azure OpenAI":
        return AzureChatOpenAI(
            azure_deployment=model_name,
            openai_api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=api_key or settings.AZURE_OPENAI_API_KEY
        )
    elif provider == "OpenAI":
        return ChatOpenAI(
            model=model_name,
            api_key=api_key or settings.OPENAI_API_KEY
        )
    elif provider == "Google Gemini":
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key or settings.GOOGLE_API_KEY
        )
    elif provider == "Anthropic":
        return ChatAnthropic(
            model_name=model_name,
            api_key=api_key or settings.ANTHROPIC_API_KEY
        )
    elif provider == "Minimax":
        return ChatOpenAI(
            model=model_name,
            api_key=api_key or settings.MINIMAX_API_KEY,
            base_url="https://api.minimax.chat/v1"
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
