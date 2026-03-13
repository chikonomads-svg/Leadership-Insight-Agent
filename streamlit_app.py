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

# Custom CSS for a beautiful, premium Apple-like aesthetic
st.markdown("""
<style>
    /* Main background with a clean, minimal aesthetic */
    .stApp {
        background-color: #fbfbfd;
        color: #1d1d1f;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
    }
    
    /* Headers matching Apple typography */
    h1, h2, h3 {
        color: #1d1d1f;
        font-weight: 600;
        letter-spacing: -0.015em;
        margin-bottom: 0.5rem;
    }
    
    /* User Message Bubble matching Apple style */
    .stChatMessage.user {
        background-color: #0071e3;
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 18px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0, 113, 227, 0.15);
        border: none;
    }
    .stChatMessage.user p {
        color: white;
        font-size: 1rem;
        line-height: 1.4;
    }
    
    /* Assistant Message Bubble with refined, clean look */
    .stChatMessage.assistant {
        background-color: #ffffff;
        color: #1d1d1f;
        border-radius: 18px 18px 18px 4px;
        padding: 14px 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(0,0,0,0.08);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    }
    .stChatMessage.assistant p {
        font-size: 1rem;
        line-height: 1.5;
    }
    
    /* Input Box styling container */
    .stChatInputContainer {
        padding-bottom: 2rem;
    }
    
    /* Sidebar with elegant minimal styling */
    [data-testid="stSidebar"] {
        background-color: #f5f5f7;
        border-right: 1px solid rgba(0,0,0,0.08);
    }
    
    /* Sidebar Button styling matching Apple sleekness */
    .stButton button {
        background-color: #ffffff;
        color: #1d1d1f !important;
        border: 1px solid rgba(0,0,0,0.1);
        border-radius: 980px; /* Fully rounded buttons */
        font-weight: 500;
        padding: 0.4rem 1.2rem;
        transition: all 0.2s ease;
        width: 100%;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .stButton button:hover {
        background-color: #f5f5f7;
        border-color: rgba(0,0,0,0.15);
        color: #1d1d1f !important;
    }
    .stButton button p {
        color: #1d1d1f !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: transparent !important;
        color: #1d1d1f !important;
        font-weight: 500;
        border-bottom: 1px solid rgba(0,0,0,0.08);
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
