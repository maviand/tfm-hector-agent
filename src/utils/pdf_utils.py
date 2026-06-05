import fitz  # PyMuPDF
import os

def split_pdf(file_path: str, output_dir: str, max_pages: int = 15) -> list[str]:
    """
    Splits a large PDF into smaller chunks of `max_pages` pages each.
    Returns a list of paths to the newly created PDF chunks.
    """
    if not file_path.lower().endswith(".pdf"):
        return [file_path]  # Do not split non-PDFs

    doc = fitz.open(file_path)
    total_pages = len(doc)

    if total_pages <= max_pages:
        return [file_path]

    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.basename(file_path)
    name_no_ext = os.path.splitext(base_name)[0]

    chunk_paths = []
    
    for start_page in range(0, total_pages, max_pages):
        end_page = min(start_page + max_pages - 1, total_pages - 1)
        
        # Create a new blank document
        chunk_doc = fitz.open()
        chunk_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)
        
        chunk_filename = f"{name_no_ext}_part{start_page // max_pages + 1}.pdf"
        chunk_path = os.path.join(output_dir, chunk_filename)
        
        chunk_doc.save(chunk_path)
        chunk_doc.close()
        
        chunk_paths.append(chunk_path)

    doc.close()
    return chunk_paths
