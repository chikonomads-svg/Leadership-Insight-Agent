import asyncio
import argparse
import sys
from src.config.settings import settings
from src.ingestion.document_parser import parse_all_documents
from src.vectorstore.faiss_store import build_faiss_index
from src.agent.rag_chain import LeadershipInsightAgent

async def run_ingestion():
    print(f"--- Starting Ingestion Pipeline for '{settings.DATA_DIR}' ---")
    documents = await parse_all_documents(settings.DATA_DIR)
    
    if not documents:
        print("No documents were parsed successfully. Check for files in the data directory and ensure dependencies are installed.")
        return
        
    print("\n--- Constructing FAISS Index ---")
    await build_faiss_index(documents)
    print("\n✅ Ingestion Pipeline Complete.")

async def run_cli():
    print("Initializing Leadership Insight Agent...")
    try:
        agent = LeadershipInsightAgent()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run ingestion first using: python main.py --ingest")
        return
        
    print("Welcome to the AI Leadership Insight Agent.")
    print("Type your questions below. Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            user_input = input("\nLeadership Question: ")
            if user_input.lower() in ('exit', 'quit'):
                break
            if not user_input.strip():
                continue
                
            print("\nAgent is thinking...")
            answer = await agent.aask(user_input)
            print("-" * 50)
            print(f"Answer:\n{answer}")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred during query execution: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apple AI Leadership Insight Agent")
    parser.add_argument("--ingest", action="store_true", help="Run the document extraction and vectorization pipeline")
    
    args = parser.parse_args()
    
    # We must use asyncio.run() to properly fire up the async event loop at the root level
    if args.ingest:
        asyncio.run(run_ingestion())
    else:
        asyncio.run(run_cli())
