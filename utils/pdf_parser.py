import os
from datetime import datetime

import PyPDF2


def is_pdf_file(file_path):
    return bool(file_path) and file_path.lower().endswith(".pdf")


def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    return text


def get_file_info(file_path):
    size_bytes = os.path.getsize(file_path)
    size_kb = size_bytes / 1024
    return {
        "path": file_path,
        "name": os.path.basename(file_path),
        "size": f"{size_kb:.1f} KB",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def preview_text(text, limit=300):
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit].rstrip() + "..."
