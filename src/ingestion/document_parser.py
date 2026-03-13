import os
import glob
import asyncio
import aiofiles
from .pdf_extractor import extract_text_and_tables
from .image_extractor import extract_large_images_with_ocr

async def process_markdown(file_path: str) -> str:
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
        return await f.read()

async def process_pdf(file_path: str) -> str:
    # Run text/table extraction and image/OCR extraction concurrently
    text_result, ocr_result = await asyncio.gather(
        extract_text_and_tables(file_path),
        extract_large_images_with_ocr(file_path)
    )
    
    combined = f"--- START OF DOCUMENT: {os.path.basename(file_path)} ---\n"
    if text_result:
        combined += f"\n[TEXT & TABLES]\n{text_result}\n"
    if ocr_result:
        combined += f"\n[IMAGE OCR RESULTS]\n{ocr_result}\n"
        
    combined += f"--- END OF DOCUMENT: {os.path.basename(file_path)} ---\n"
    return combined

async def parse_all_documents(data_dir: str) -> list[dict]:
    """
    Finds all supported documents in data_dir, extracts their content asynchronously,
    and returns a list of dictionaries with metadata and content.
    """
    pdf_files = glob.glob(f"{data_dir}/**/*.pdf", recursive=True)
    md_files = glob.glob(f"{data_dir}/**/*.md", recursive=True)
    
    tasks = []
    metadata_list = []
    for pdf in pdf_files:
        tasks.append(process_pdf(pdf))
        # Example Path: data/FISCAL YEAR 2024/Quarterly Reports/Q1 2024 (10-Q) - Dec 30, 2023.pdf
        fy = "2024" if "2024" in pdf else "2025" if "2025" in pdf else "Other"
        doc_type = "Annual Report" if "Annual Report" in pdf else "Quarterly Report" if "Quarterly Reports" in pdf else "Earnings Report" if "Earnings" in pdf else "Unknown"
        quarter = "Q1" if "Q1" in pdf else "Q2" if "Q2" in pdf else "Q3" if "Q3" in pdf else "Q4" if "Q4" in pdf else "Full Year"
        
        metadata_list.append({
            "source": pdf, 
            "type": "pdf",
            "fiscal_year": fy,
            "document_type": doc_type,
            "quarter": quarter,
            "filename": os.path.basename(pdf)
        })
        
    for md in md_files:
        tasks.append(process_markdown(md))
        fy = "2024" if "2024" in md else "2025" if "2025" in md else "Other"
        doc_type = "Strategy Notes" if "strategy" in md.lower() else "Operational Updates" if "operational" in md.lower() else "Unknown"
        
        metadata_list.append({
            "source": md, 
            "type": "markdown",
            "fiscal_year": fy,
            "document_type": doc_type,
            "quarter": "Full Year", # Summaries cover the whole FY
            "filename": os.path.basename(md)
        })
        
    print(f"Starting async ingestion for {len(tasks)} documents...")
    # Gather all results concurrently with a progress bar
    from tqdm.asyncio import tqdm
    results = await tqdm.gather(*tasks, desc="Extracting Documents (PDF/MD)")
    
    documents = []
    for meta, content in zip(metadata_list, results):
        if isinstance(content, Exception):
            print(f"Error processing {meta['source']}: {content}")
        elif content: # omit empty
            documents.append({
                "page_content": content,
                "metadata": meta
            })
            
    print(f"Successfully processed {len(documents)} documents.")
    return documents
