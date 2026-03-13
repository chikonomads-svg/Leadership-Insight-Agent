import os
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.embeddings.azure_embedder import get_azure_embeddings
from src.config.settings import settings

async def build_faiss_index(raw_documents: list[dict]):
    """
    Chunks the extracted strings and builds a FAISS index, saving it to disk.
    Called once during ingestion.
    """
    embedder = get_azure_embeddings()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=250
    )
    
    docs = []
    for doc in raw_documents:
        # langchain expects `Document` objects
        docs.append(Document(page_content=doc["page_content"], metadata=doc["metadata"]))
        
    print(f"Splitting {len(docs)} large documents into chunks...")
    chunks = text_splitter.split_documents(docs)
    print(f"Created {len(chunks)} chunks.")
    
    print("Embedding chunks and building FAISS index with parallel batching (this may take a while)...")
    
    # Explicitly batch the chunks for parallel processing
    batch_size = 100
    batches = [chunks[i:i + batch_size] for i in range(0, len(chunks), batch_size)]
    
    async def process_batch(batch_chunks):
        texts = [chunk.page_content for chunk in batch_chunks]
        # aembed_documents uses the async Azure OpenAI client
        embeddings = await embedder.aembed_documents(texts)
        # Return tuples of (text, embedding, metadata)
        return list(zip(texts, embeddings, [chunk.metadata for chunk in batch_chunks]))

    print(f"Processing {len(batches)} batches concurrently...")
    
    # Run all batches concurrently with a progress bar
    import asyncio
    from tqdm.asyncio import tqdm
    batch_results = await tqdm.gather(*(process_batch(b) for b in batches), desc="Generating Embeddings")
    
    all_text_embeddings = []
    all_metadatas = []
    
    for i, res in enumerate(batch_results):
        if isinstance(res, Exception):
            print(f"Error processing batch {i}: {res}")
        else:
            for text, emb, meta in res:
                all_text_embeddings.append((text, emb))
                all_metadatas.append(meta)
            
    print("Initializing FAISS store from generated embeddings...")
    vectorstore = FAISS.from_embeddings(
        text_embeddings=all_text_embeddings,
        embedding=embedder,
        metadatas=all_metadatas
    )
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)
    vectorstore.save_local(settings.FAISS_INDEX_PATH)
    print(f"FAISS index saved successfully at {settings.FAISS_INDEX_PATH}")

def load_faiss_index() -> FAISS:
    """
    Loads the saved FAISS index from disk.
    """
    if not os.path.exists(settings.FAISS_INDEX_PATH):
        raise FileNotFoundError(f"FAISS index not found at {settings.FAISS_INDEX_PATH}. Please run ingestion first.")
        
    embedder = get_azure_embeddings()
    return FAISS.load_local(settings.FAISS_INDEX_PATH, embedder, allow_dangerous_deserialization=True)
