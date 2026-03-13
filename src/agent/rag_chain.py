from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from src.vectorstore.faiss_store import load_faiss_index
from src.agent.llm_client import get_chat_model

class LeadershipInsightAgent:
    def __init__(self, provider: str = "Azure OpenAI", model_name: str = "", api_key: str = None):
        # Load the index and initialize the model once
        self.vectorstore = load_faiss_index()
        # Search kwargs can be adjusted (e.g., k=4 limits to top 4 chunks)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
        self.llm = get_chat_model(provider, model_name, api_key)
        
        # Define the system prompt instruction
        template = """You are an AI Leadership Insight Agent for Apple.
        You have been provided with context from internal documents (Annual Reports, Quarterly Reports, Strategy Notes, Operational Updates).
        Use the following pieces of retrieved context to answer the question concisely and accurately. 
        If you don't know the answer based ONLY on the provided context, just say that you don't know. 
        Do not make up information. Be professional and factual.
        
        IMPORTANT FORMATTING RULES:
        1. STRONGLY PREFER using bullet points to break down complex periods, comparisons, and numbers.
        2. Make the response highly readable and easy to scan.
        3. DO NOT format numbers, metrics, or currencies with backticks or inline code blocks (e.g., write 81,797, not `81,797`).
        4. DO NOT include citations or reference tags in your text (e.g. no [1], no [Source: ...]). Just write the plain answer. I will handle citations separately.

        Context: 
        {context}

        Question: {question}

        Answer:"""
        
        self.prompt = ChatPromptTemplate.from_template(template)
        
        # We'll handle the chain slightly differently to return the source documents
        self.qa_chain = self.prompt | self.llm | StrOutputParser()

    async def aask(self, question: str) -> dict:
        """
        Asynchronously invoke the RAG chain and return both the answer and the source documents.
        """
        # 1. Retrieve the documents
        docs = await self.retriever.ainvoke(question)
        
        # 2. Format the documents for the prompt
        formatted_context = []
        for i, doc in enumerate(docs):
            meta = doc.metadata
            header = f"[Source {i+1}: {meta.get('filename', 'Unknown')}, FY: {meta.get('fiscal_year', 'Unknown')}, Q: {meta.get('quarter', 'Unknown')}, Type: {meta.get('document_type', 'Unknown')}]"
            formatted_context.append(f"{header}\n{doc.page_content}")
            
        context_str = "\n\n".join(formatted_context)
        
        # 3. Generate the answer
        answer = await self.qa_chain.ainvoke({"context": context_str, "question": question})
        
        return {
            "answer": answer,
            "source_documents": docs
        }
