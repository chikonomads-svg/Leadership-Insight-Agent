from langchain_openai import AzureOpenAIEmbeddings
from src.config.settings import settings

def get_azure_embeddings() -> AzureOpenAIEmbeddings:
    """
    Initializes and returns the AzureOpenAIEmbeddings instance based on settings.
    LangChain's embedder has async methods (.aembed_documents, .aembed_query) natively.
    """
    return AzureOpenAIEmbeddings(
        azure_deployment=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        openai_api_version=settings.AZURE_OPENAI_EMBEDDING_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY
    )
