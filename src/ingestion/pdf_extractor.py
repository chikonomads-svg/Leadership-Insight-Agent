import asyncio
import pdfplumber

async def extract_text_and_tables(pdf_path: str) -> str:
    """
    Asynchronously extracts raw text and table structures perfectly from a PDF file.
    """
    def _extract():
        results = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_number = i + 1
                    results.append(f"--- PAGE {page_number} ---")
                    
                    # Extract raw text
                    text = page.extract_text()
                    if text:
                        results.append(text.strip())
                    
                    # Extract tables separately to keep format
                    tables = page.extract_tables()
                    if tables:
                        results.append(f"--- TABLES ON PAGE {page_number} ---")
                        for table_index, table in enumerate(tables):
                            results.append(f"Table {table_index + 1}:")
                            for row in table:
                                # Replace None with empty string and join rows nicely
                                cleaned_row = [str(cell).replace("\n", " ").strip() if cell is not None else "" for cell in row]
                                results.append(" | ".join(cleaned_row))
                        results.append("") # Empty line after tables
                        
            return "\n".join(results)
        except Exception as e:
            return f"Error processing PDF text/tables from {pdf_path}: {str(e)}"
            
    # Run blocking pdfplumber code in a thread
    return await asyncio.to_thread(_extract)
