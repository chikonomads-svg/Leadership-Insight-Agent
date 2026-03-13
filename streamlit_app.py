import streamlit as st
import asyncio
from src.agent.rag_chain import LeadershipInsightAgent
from src.agent.chart_generator import ChartGenerator
from src.ui.formatter import render_chart
from src.ui.model_selector import render_model_selector

# Initialize the Streamlit page configuration
st.set_page_config(
    page_title="Apple Leadership Insights",
    page_icon="🍎",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom CSS for a beautiful, colorful, and vibrant aesthetic
st.markdown("""
<style>
    /* Main background with a vibrant, subtle gradient */
    .stApp {
        background: linear-gradient(180deg, #ffffff 0%, #ffe8e8 100%);
        color: #1a1a1a;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Headers with dynamic gradient text */
    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin-bottom: 0.5rem;
    }
    
    /* User Message Bubble with vibrant gradient */
    .stChatMessage.user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px 20px 0px 20px;
        padding: 15px 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.2);
        border: none;
        transition: transform 0.2s ease;
    }
    .stChatMessage.user p {
        color: white;
        font-size: 1.05rem;
    }
    .stChatMessage.user:hover {
        transform: translateY(-2px);
    }
    
    /* Assistant Message Bubble with crisp glassmorphism */
    .stChatMessage.assistant {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        color: #2b2b2b;
        border-radius: 20px 20px 20px 0px;
        padding: 15px 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.4);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.05);
        transition: transform 0.2s ease;
    }
    .stChatMessage.assistant:hover {
        transform: translateY(-2px);
    }
    
    /* Input Box styling container */
    .stChatInputContainer {
        padding-bottom: 2rem;
    }
    
    /* Sidebar with colorful gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #ffe8e8 100%);
        border-right: 1px solid rgba(255,107,107,0.2);
        box-shadow: 2px 0 15px rgba(255,107,107,0.1);
    }
    
    /* Sidebar Button styling */
    .stButton button {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
        color: white !important;
    }
    .stButton button p {
        color: white !important;
    }
    
    /* Expander styling - API Config Area */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%) !important;
        color: #1d1d1f !important;
        font-weight: 800;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 5px;
    }
    
    div[data-testid="stExpanderDetails"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(5px);
        border: 2px solid #ff9a9e !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }
    
    /* API Input Fields */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 2px solid #4ECDC4 !important;
        border-radius: 10px !important;
        color: #1a1a1a !important;
        font-weight: 500;
    }
    .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus {
        border-color: #FF6B6B !important;
        box-shadow: 0 0 10px rgba(255, 107, 107, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# Application Header
st.title("🍎 Apple Leadership Insights")
st.markdown("Ask questions about Apple's strategy, financials, and operations based on recent FY24 & FY25 corporate documents.")

# Sidebar information
with st.sidebar:
    st.header("About")
    st.info(
        "This is an AI Leadership Insight Agent powered by **Azure OpenAI** and **RAG** (Retrieval-Augmented Generation).\n\n"
        "It uses a local FAISS vector store containing text and OCR'd images from Apple's official SEC filings and strategic updates."
    )
    
    st.divider()
    model_changed = render_model_selector()
    
    st.divider()
    st.markdown("### Knowledge Base")
    st.markdown("- FY 2024 & 2025 Annual Reports (10-K)\n- Quarterly Reports (10-Q)\n- Earnings Releases\n- Strategy Notes (MD)\n- Operational Updates (MD)")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Initialize the agent and chat history in session state
if "agent" not in st.session_state or model_changed:
    with st.spinner(f"Initializing {st.session_state.llm_provider} AI Agent..."):
        try:
            st.session_state.agent = LeadershipInsightAgent(
                provider=st.session_state.llm_provider, 
                model_name=st.session_state.llm_model_name,
                api_key=st.session_state.llm_api_key_override or None
            )
            st.session_state.chart_gen = ChartGenerator(
                provider=st.session_state.llm_provider, 
                model_name=st.session_state.llm_model_name,
                api_key=st.session_state.llm_api_key_override or None
            )
        except FileNotFoundError:
            st.error("Knowledge base not found. Please run the ingestion pipeline first via `python main.py --ingest`")
            st.stop()
            
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "chart_config" in message:
            render_chart(message["chart_config"])

# Handle user input
if prompt := st.chat_input("Ask a question about Apple's strategy or operations..."):
    # Add user message to chat history and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        with st.spinner("Analyzing documents..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                # The agent now returns a dict with 'answer' and 'source_documents'
                result = loop.run_until_complete(st.session_state.agent.aask(prompt))
                
                answer_text = result["answer"]
                docs = result["source_documents"]
                
                # Append citation numbers at the end of the text
                citation_links = " ".join([f"[{i+1}]" for i in range(len(docs))])
                if citation_links:
                    answer_text += f"\n\n**Sources:** {citation_links}"
                
                response_placeholder.markdown(answer_text)
                
                # Render source document details inside a single dropdown
                if docs:
                    with st.expander("Source Details"):
                        for i, doc in enumerate(docs):
                            meta = doc.metadata
                            st.markdown(f"**Source [{i+1}]: {meta.get('filename', 'UnknownDocument')} ({meta.get('document_type', 'N/A')})**")
                            st.markdown(f"**Fiscal Year:** {meta.get('fiscal_year', 'N/A')} | **Quarter:** {meta.get('quarter', 'N/A')}")
                            st.text(doc.page_content[:1500] + ("..." if len(doc.page_content) > 1500 else ""))
                            if i < len(docs) - 1:
                                st.divider()
                
                # Ensure UI completes the answer rendering sequentially
                
                # Fetch chart configuration from the LLM based on its answer
                with st.spinner("Generating visualization..."):
                    chart_config = loop.run_until_complete(st.session_state.chart_gen.agenerate(answer_text))
                    render_chart(chart_config)
                
                # Add assistant response to history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer_text,
                    "chart_config": chart_config
                })
            except Exception as e:
                response_placeholder.error(f"An error occurred: {str(e)}")
            finally:
                loop.close()
