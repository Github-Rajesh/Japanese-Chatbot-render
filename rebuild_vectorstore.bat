@echo off
echo ================================================
echo Japanese Chatbot - Rebuild Vector Database
echo ================================================
echo.
echo This will delete the existing vector database and
echo rebuild it with all documents from the knowledge base,
echo including subdirectories and vertical Japanese PDFs.
echo.
pause

echo.
echo [1/2] Deleting existing vectorstore...
if exist "data\vectorstore" (
    rmdir /s /q "data\vectorstore"
    echo ✓ Vectorstore deleted
) else (
    echo ℹ No existing vectorstore found
)

echo.
echo [2/2] The vectorstore will be rebuilt automatically
echo when you start the backend.
echo.
echo To start the backend now, run: start_backend.bat
echo.
pause

