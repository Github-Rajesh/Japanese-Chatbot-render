# Updates Summary - Subdirectory Support & Vertical Japanese PDFs

## Overview
The chatbot has been updated to support:
1. **Recursive subdirectory scanning** - Automatically loads documents from all subfolders in the knowledge base
2. **Vertical Japanese PDF support** - Uses OCR (Tesseract) to handle PDFs with vertical Japanese text

## Changes Made

### 1. Backend Updates

#### `backend/rag_system.py`
- **Added**: Import for `vertical_japanese` module
- **Added**: `_load_vertical_pdf()` method to handle vertical Japanese PDFs using OCR
- **Modified**: `create_vectorstore()` to:
  - Use `rglob()` instead of `glob()` for recursive subdirectory search
  - Automatically detect PDFs in "Verticle writing" folder and process them with OCR
  - Display relative paths from knowledge base when loading files
  - Support for all file types (PDF, Excel) in any subdirectory

#### `backend/vertical_japanese.py` (renamed from `vertical Japanese.py`)
- **Renamed**: File renamed to use underscores for proper Python imports
- **Added**: `_configure_tesseract()` function for automatic Tesseract path detection
- **Improved**: Cross-platform support (Windows, macOS, Linux)
- **Added**: Graceful error handling when Tesseract is not installed
- **Added**: Availability checks in extraction functions
- **Features**:
  - Automatic Tesseract path detection across common installation locations
  - OCR support for vertical Japanese text (jpn_vert)
  - Text cleaning and normalization for Japanese characters
  - Per-page document creation with metadata

### 2. Configuration Files

#### `requirements.txt`
- **Added**: `pytesseract==0.3.10` - Python wrapper for Tesseract OCR
- **Added**: `pdf2image==1.17.0` - PDF to image conversion
- **Added**: `Pillow==10.2.0` - Image processing library

### 3. Documentation

#### `README.md`
- **Added**: Prerequisites for Tesseract OCR and Poppler
- **Added**: Installation instructions for Tesseract and Poppler
- **Updated**: Project structure to show subdirectories
- **Added**: Feature list includes subdirectory support and vertical Japanese PDFs
- **Updated**: Tech stack to mention OCR capabilities
- **Added**: Section on rebuilding the knowledge base after reorganization

### 4. Helper Scripts

#### `rebuild_vectorstore.bat` (NEW)
- **Purpose**: Easy way to rebuild the vector database after reorganizing files
- **Features**:
  - Deletes existing vectorstore
  - Provides instructions for rebuilding
  - User-friendly prompts and confirmations

## Knowledge Base Structure

The new structure supports subdirectories:

```
knowledge base main/
├── Drawing docs/       # Drawing documents (PDFs)
├── Excel/              # Excel files (.xlsx)
├── Normal/             # Standard PDFs
└── Verticle writing/   # Vertical Japanese PDFs (uses OCR)
```

## How It Works

### Subdirectory Support
- The system now uses `Path.rglob("*.pdf")` and `Path.rglob("*.xlsx")` to recursively find all files
- Files are loaded regardless of directory depth
- Relative paths are displayed for better tracking

### Vertical Japanese PDF Processing
1. **Detection**: PDFs in folders named "Verticle writing" or "Vertical writing" are automatically detected
2. **OCR Processing**: 
   - PDF is converted to images (300 DPI by default)
   - Tesseract OCR with `jpn_vert` language model processes each page
   - Text is cleaned and normalized for better quality
3. **Fallback**: If OCR fails, the system falls back to standard PDF loader
4. **Metadata**: Each page includes metadata: source, page number, type, total pages

## Prerequisites for Users

### Required Software
1. **Tesseract OCR** - For vertical Japanese PDF support
   - Windows: https://github.com/UB-Mannheim/tesseract/wiki
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`
   - **Important**: Install Japanese language data (jpn and jpn_vert)

2. **Poppler** - For PDF to image conversion (Windows)
   - Download: https://github.com/oschwartz10612/poppler-windows/releases/
   - Add `bin` folder to system PATH

### Python Dependencies
Run `pip install -r requirements.txt` to install:
- pytesseract
- pdf2image
- Pillow
- (all other existing dependencies)

## How to Rebuild the Vector Database

Since files have been reorganized into subdirectories, users should rebuild their vector database:

### Option 1: Quick Method
```bash
rebuild_vectorstore.bat
```

### Option 2: Manual Method
```bash
# Delete existing vectorstore
rmdir /s /q "data\vectorstore"

# Restart backend (will auto-rebuild)
start_backend.bat
```

## Performance Notes

- **Standard PDFs**: Load quickly using PyPDFLoader
- **Vertical Japanese PDFs**: Take longer due to OCR processing
  - ~1-3 seconds per page depending on content
  - Higher DPI = better accuracy but slower processing
- **First run**: Will take longer to index all documents
- **Subsequent runs**: Uses cached vectorstore for fast retrieval

## Technical Details

### OCR Configuration
- **Language Model**: jpn_vert (Japanese vertical text)
- **DPI**: 300 (default, configurable)
- **PSM Mode**: 5 (assume single uniform block of text)
- **Text Cleaning**: Removes extra spaces, normalizes characters

### Document Metadata
Standard PDFs:
- source: file path
- page: page number
- (standard PyPDF metadata)

Vertical Japanese PDFs:
- source: file path
- page: page number
- type: "vertical_japanese"
- total_pages: total page count

## Error Handling

The system includes robust error handling:
1. **Tesseract not found**: Falls back to standard PDF loader with warning
2. **OCR fails**: Falls back to standard PDF loader for that file
3. **Missing files**: Logs error and continues with other files
4. **Empty documents**: Skips empty pages to save space

## Backward Compatibility

- Existing functionality is preserved
- Standard PDFs still use the fast PyPDFLoader
- No changes required for users without vertical Japanese PDFs
- System works with or without Tesseract (just disables OCR feature)

## Testing Recommendations

1. **Test with standard PDFs**: Verify normal operation
2. **Test with vertical Japanese PDFs**: Check OCR quality
3. **Test with mixed folder structure**: Ensure all files are found
4. **Test rebuild process**: Verify vectorstore recreation works
5. **Test without Tesseract**: Verify graceful fallback

## Future Enhancements

Potential improvements:
- Support for more file types (Word, PowerPoint, etc.)
- Parallel processing for faster OCR
- OCR quality optimization
- Custom OCR settings per folder
- Progress bars for long operations
- Caching of OCR results

