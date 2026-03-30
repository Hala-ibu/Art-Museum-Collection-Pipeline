import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from utils.logger import logging  
from storage.mongo import save_to_mongo 
from api.client import fetch_movies
from parsing.parsers import (
    extract_text_from_pdf,
    extract_text_from_two_column_pdf,
    extract_text_from_word,
    extract_data_from_excel,
    extract_summary_from_excel
)
def run_pipeline():

    pdf_standard = "data/raw/pdf/art_tables_documentpdf.pdf"
    pdf_two_column = "data/raw/pdf/art_tables_documentpdf.pdf" 
    #still i dont have a double column one

    text_standard = extract_text_from_pdf(pdf_standard)
    save_to_mongo(
        {"text": text_standard},
        "PDF Source",
        {"file_name": "art_tables_documentpdf.pdf", "type": "pdf"}
    )

    text_two_column = extract_text_from_two_column_pdf(pdf_two_column)
    save_to_mongo(
        {"text": text_two_column},
        "PDF Source",
        {"file_name": "art_tables_documentpdf.pdf", "type": "pdf"}
    )

    logging.info("PDF data processed")

    word_standard = "data/raw/word/art_tables_document.docx"
    word_two_column = "data/raw/word/art_tables_document.docx"
    #still i dont have a double column one

    text_word = extract_text_from_word(word_standard)
    save_to_mongo(
        {"text": text_word},
        "Word Source",
        {"file_name": "art_tables_document.docx", "type": "word"}
    )

    text_word_2 = extract_text_from_word(word_two_column)
    save_to_mongo(
        {"text": text_word_2},
        "Word Source",
        {"file_name": "art_tables_document.docx", "type": "word"}
    )

    logging.info("Word data processed")


    excel_path = "data/raw/excel/Book1.xlsx"
    art_excel = extract_data_from_excel(excel_path)

    for art in art_excel:
        save_to_mongo(
            art,
            "Excel Source",
            {"file_name": "Book1.xlsx", "type": "excel"}
        )

    summary = extract_summary_from_excel(excel_path)
    save_to_mongo(
        summary,
        "Excel Summary",
        {"file_name": "Book1.xlsx", "type": "excel_summary"}
    )

    logging.info("Excel data processed")

    logging.info("Pipeline finished successfully")

if __name__ == "__main__":
    run_pipeline()