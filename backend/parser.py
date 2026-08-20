import os
from pathlib import Path
import pymupdf
from models import ExtractedDocument, PDFPageContent

class PDFParserService:
    """ Service responsible for reading PDFs and preserving page-level boundaries."""
    
    @staticmethod
    def extract_from_path(file_path:str) -> ExtractedDocument:
        """ Parses a local PDF file into structured page records. 
        
        Args:
            file_path: Relative or absolute path to the .pdf file.
        
        Returns:
            ExtractedDocument containing all extracted pages with metadata.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found at {file_path}")
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"File {file_path} is not a valid pdf document.")
        
        doc = pymupdf.open(str(path))
        extracted_pages : list[PDFPageContent] = []
        
        try:
            total_pages = len(doc)
            
            for page_index, page in enumerate(doc, start=1):
                # Extract text preserving reading order
                text = page.get_text("text").strip()

                page_record = PDFPageContent(
                    page_number=page_index,
                    raw_text=text,
                    character_count=len(text),
                    is_empty=len(text) == 0,
                )
                extracted_pages.append(page_record)
            return ExtractedDocument(
                filename=path.name,
                total_pages=total_pages,
                pages=extracted_pages,
            )
        finally:
            doc.close()
            
    @staticmethod
    def extract_from_bytes(file_bytes:bytes, filename: str = "uploaded_document.pdf") -> ExtractedDocument:
        """ Parses a PDF provided as raw bytes (used for incoming FastAPI uploads)
        
        Args:
            file_bytes: Raw binary payload of the PDF file.
            file_name: Original file name from the upload server.
            
        Returns:
            ExtractedDocument containing structured page records.
        
        """           
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        extracted_pages : list[PDFPageContent] = []
        
        try:
            total_pages = len(doc)
            
            for page_index, page in enumerate(doc, start=1):
                text = page.get_text("text").strip()
                
                page_record = PDFPageContent(
                    page_number=page_index,
                    raw_text=text,
                    character_count=len(text),
                    is_empty=len(text)==0,
                )
                extracted_pages.append(page_record)
                
            return ExtractedDocument(
                filename=filename,
                total_pages=total_pages,
                pages = extracted_pages,
            )
            
        finally:
            doc.close()
            
            
            
# def main():
#     file_name = 'input/Easy/PDF_Deid_Deidentification_0.pdf'
    
#     doc = PDFParserService.extracted_from_path(file_name)
#     pages = doc.pages
    
    
#     print(f"File name : {doc.filename}")
#     print(f"Total_pages: {doc.total_pages}")
    
#     for page in pages:
#         print(f"{page.page_number}")
#         print(f"{page.raw_text}")
    
                
# if __name__ == "__main__":
#     main()
    