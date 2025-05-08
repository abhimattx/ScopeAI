import fitz  # PyMuPDF
from typing import Union
from io import BytesIO

def extract_pdf_text(uploaded_pdf: Union[BytesIO, any]) -> str:
    """
    Extracts text content from a PDF file using PyMuPDF (fitz).
    
    Args:
        uploaded_pdf: Uploaded file from Streamlit uploader
    
    Returns:
        str: Extracted plain text from the PDF
    """
    try:
        text = ""
        with fitz.open(stream=uploaded_pdf.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text if text.strip() else "❌ No readable text found in PDF."
    
    except Exception as e:
        return f"❌ Failed to extract text from PDF: {str(e)}"
