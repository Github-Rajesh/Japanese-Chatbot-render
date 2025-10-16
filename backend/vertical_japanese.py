import pytesseract
from PIL import Image
import re
from pdf2image import convert_from_path
import os
import sys
import shutil

# Configure Tesseract path
def _configure_tesseract():
    """Automatically configure Tesseract path based on platform and installation"""
    # Check if tesseract is already in PATH
    if shutil.which('tesseract'):
        return True
    
    # Common Tesseract installation paths
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"/usr/bin/tesseract",
        r"/usr/local/bin/tesseract",
        r"/opt/homebrew/bin/tesseract"
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"✓ Found Tesseract at: {path}")
            return True
    
    print("WARNING: Tesseract OCR not found. Please install Tesseract:")
    print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
    print("  macOS: brew install tesseract")
    print("  Linux: sudo apt-get install tesseract-ocr")
    return False

# Try to configure Tesseract on module load
_tesseract_available = _configure_tesseract()


def clean_japanese_text(text):
    """Clean and normalize Japanese OCR text"""
    # Remove extra spaces between Japanese characters
    text = re.sub(r'\s+', '', text)
    
    # Normalize OCR misreads (optional custom fixes)
    text = text.replace("O", "〇")
    
    return text


def extract_text_from_pdf(pdf_path, lang="jpn_vert", dpi=300, clean_text=False, save_to_file=False):
    """
    Extract text from a PDF file using OCR.
    
    Args:
        pdf_path (str): Path to the PDF file
        lang (str): Tesseract language model (default: "jpn_vert" for vertical Japanese)
        dpi (int): DPI resolution for PDF to image conversion (default: 300)
        clean_text (bool): Whether to clean/normalize the text (default: False)
        save_to_file (bool): Whether to save output to a text file (default: False)
    
    Returns:
        dict: Dictionary containing:
            - 'success' (bool): Whether extraction was successful
            - 'text' (str): Combined text from all pages
            - 'pages' (list): List of text per page
            - 'page_count' (int): Number of pages processed
            - 'error' (str): Error message if any
            - 'output_file' (str): Path to saved file if save_to_file=True
    """
    # Check if Tesseract is available
    if not _tesseract_available:
        return {
            'success': False,
            'text': '',
            'pages': [],
            'page_count': 0,
            'error': 'Tesseract OCR is not installed or not found in PATH',
            'output_file': None
        }
    
    try:
        # Convert PDF pages to images
        images = convert_from_path(pdf_path, dpi=dpi)
        page_count = len(images)
        
        # Process each page
        all_text = []
        pages_text = []
        
        for i, img in enumerate(images, start=1):
            # OCR with specified language model
            text = pytesseract.image_to_string(img, lang=lang, config="--psm 5")
            
            # Clean text if requested
            if clean_text:
                text = clean_japanese_text(text)
            
            pages_text.append(text)
            all_text.append(f"--- Page {i} ---\n{text}\n")
        
        # Combine all pages
        combined_text = "\n".join(all_text)
        
        # Save to file if requested
        output_file = None
        if save_to_file:
            output_file = pdf_path.replace(".pdf", "_ocr_output.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(combined_text)
        
        return {
            'success': True,
            'text': combined_text,
            'pages': pages_text,
            'page_count': page_count,
            'error': None,
            'output_file': output_file
        }
    
    except Exception as e:
        return {
            'success': False,
            'text': '',
            'pages': [],
            'page_count': 0,
            'error': str(e),
            'output_file': None
        }


def extract_text_from_image(image_path, lang="jpn_vert", clean_text=False):
    """
    Extract text from a single image file using OCR.
    
    Args:
        image_path (str): Path to the image file
        lang (str): Tesseract language model (default: "jpn_vert" for vertical Japanese)
        clean_text (bool): Whether to clean/normalize the text (default: False)
    
    Returns:
        dict: Dictionary containing:
            - 'success' (bool): Whether extraction was successful
            - 'text' (str): Extracted text
            - 'error' (str): Error message if any
    """
    # Check if Tesseract is available
    if not _tesseract_available:
        return {
            'success': False,
            'text': '',
            'error': 'Tesseract OCR is not installed or not found in PATH'
        }
    
    try:
        # Open image
        img = Image.open(image_path)
        
        # OCR with specified language model
        text = pytesseract.image_to_string(img, lang=lang, config="--psm 5")
        
        # Clean text if requested
        if clean_text:
            text = clean_japanese_text(text)
        
        return {
            'success': True,
            'text': text,
            'error': None
        }
    
    except Exception as e:
        return {
            'success': False,
            'text': '',
            'error': str(e)
        }


# Example usage (for testing)
if __name__ == "__main__":
    # Example 1: Extract from PDF
    pdf_path = r"C:\Users\shraj\Downloads\your_file.pdf"
    result = extract_text_from_pdf(pdf_path, save_to_file=True)
    
    if result['success']:
        print(f"Successfully processed {result['page_count']} pages")
        print(result['text'])
        if result['output_file']:
            print(f"\nText saved to: {result['output_file']}")
    else:
        print(f"Error: {result['error']}")
    
    # Example 2: Extract from image
    # image_path = r"C:\Users\shraj\Downloads\image.png"
    # result = extract_text_from_image(image_path)
    # if result['success']:
    #     print(result['text'])
    # else:
    #     print(f"Error: {result['error']}")