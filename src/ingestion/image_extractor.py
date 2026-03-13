import asyncio
import io
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

async def extract_large_images_with_ocr(pdf_path: str, min_width: int = 200, min_height: int = 200) -> str:
    """
    Asynchronously extracts images from a PDF, filters them by size, and runs OCR on the large ones.
    """
    def _extract():
        ocr_results = []
        try:
            doc = fitz.open(pdf_path)
            for page_index in range(len(doc)):
                page = doc[page_index]
                image_list = page.get_images(full=True)
                
                for img_index, img_info in enumerate(image_list):
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Convert bytes to PIL Image
                    image = Image.open(io.BytesIO(image_bytes))
                    width, height = image.size
                    
                    # Filter out small images and icons
                    if width >= min_width and height >= min_height:
                        # Run OCR
                        text = pytesseract.image_to_string(image)
                        cleaned_text = text.strip()
                        if cleaned_text:
                            ocr_results.append(
                                f"--- OCR FROM IMAGE ON PAGE {page_index+1} ---\n{cleaned_text}\n"
                            )
            return "\n".join(ocr_results)
        except Exception as e:
            return f"Error extracting images/OCR from {pdf_path}: {str(e)}"

    # Run blocking PyMuPDF/PyTesseract code in a thread pool
    return await asyncio.to_thread(_extract)
