import streamlit as st
from src.config.settings import settings

DEFAULT_MODELS = {
    "Azure OpenAI": settings.AZURE_OPENAI_CHAT_DEPLOYMENT or "gpt-5-mini",
    "OpenAI": "gpt-4o",
    "Google Gemini": "gemini-1.5-pro",
    "Anthropic": "claude-3-5-sonnet-20240620",
    "Minimax": "abab6.5s-chat" # Standard 6.5s Chat model
}

def render_model_selector() -> bool:
    """
    Renders the model selection UI using text inputs as per user request.
    Returns True if the selected model, provider, or API key changed.
    """
    if "llm_provider" not in st.session_state:
        st.session_state.llm_provider = "Azure OpenAI"
    if "llm_model_name" not in st.session_state:
        st.session_state.llm_model_name = DEFAULT_MODELS["Azure OpenAI"]
    if "llm_api_key_override" not in st.session_state:
        st.session_state.llm_api_key_override = ""
        
    old_provider = st.session_state.llm_provider
    old_model = st.session_state.llm_model_name
    old_api_key = st.session_state.llm_api_key_override
    changed = False
    
    with st.expander("🤖 LLM Configuration", expanded=False):
        # Render UI
        providers = list(DEFAULT_MODELS.keys())
        new_provider = st.selectbox(
            "Select Provider", 
            options=providers, 
            index=providers.index(old_provider) if old_provider in providers else 0
        )
        
        # Default model changes dynamically when touching the provider, if user forces change
        if new_provider != old_provider:
            st.session_state.llm_model_name = DEFAULT_MODELS[new_provider]
            
        new_model = st.text_input(
            "Enter Model Name", 
            value=st.session_state.llm_model_name,
            help="Type the strict model ID you wish to use (e.g. gpt-4o, claude-3-opus-20240229)"
        )
        
        new_api_key = st.text_input(
            f"{new_provider} API Key", 
            value=st.session_state.llm_api_key_override,
            type="password", 
            help="Leave blank to fallback to the .env file."
        )
        
        if new_provider != old_provider or new_model != old_model or new_api_key != old_api_key:
            st.session_state.llm_provider = new_provider
            st.session_state.llm_model_name = new_model
            st.session_state.llm_api_key_override = new_api_key
            changed = True
            
    return changed
