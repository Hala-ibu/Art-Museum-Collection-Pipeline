import sys
import os
import logging
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from utils.logger import logging  
from storage.mongo import save_to_mongo, build_scraped_record, build_ocr_record  
from scraping.scraper import scrape_oscar_films, scrape_multiple_pages 
from ocr.ocr_utils import ocr_scanned_pdf, compare_ocr 
from parsing.parsers import (
    extract_text_from_pdf,
    extract_text_from_word,
    extract_data_from_excel
)

def run_pipeline():
    logging.info("--- ART MUSEUM COLLECTION PIPELINE STARTING ---")

    try:
        logging.info("Processing local document files...")
        
        pdf_path = "../../data/raw/pdf/art_history.pdf"
        if os.path.exists(pdf_path):
            text = extract_text_from_pdf(pdf_path)
            save_to_mongo({"text": text}, "Local PDF", {"file_name": "art_history.pdf", "type": "pdf"})

        word_path = "../../data/raw/word/art_doc.docx"
        if os.path.exists(word_path):
            text_word = extract_text_from_word(word_path)
            save_to_mongo({"text": text_word}, "Word Source", {"file_name": "art_doc.docx", "type": "word"})

        excel_path = "../../data/raw/excel/art_inventory.xlsx"
        if os.path.exists(excel_path):
            art_data = extract_data_from_excel(excel_path)
            for item in art_data:
                save_to_mongo(item, "Excel Source", {"file_name": "art_inventory.xlsx", "type": "excel"})
                
        logging.info("Local files processed successfully.")
    except Exception as e:
        logging.error(f"Error processing local files: {e}")

    try:
        logging.info("Starting Multi-page Web Scraping...")
        teams = scrape_multiple_pages("https://www.scrapethissite.com/pages/forms/", max_pages=2)
        
        for team in teams:
            record = build_scraped_record(team, "scrapethissite.com/forms")
            save_to_mongo(record["data"], record["source"], {
                "type": record["type"],
                "extracted_at": record["extracted_at"],
                "file_name": "teams_scraped.html"
            })
        logging.info(f"Web scraping finished. Scraped {len(teams)} records.")
    except Exception as e:
        logging.error(f"Web scraping error: {e}")

    try:
        logging.info("Starting Dynamic API Scraping...")
        films = scrape_oscar_films(years=[2015])
        for film in films:
            record = build_scraped_record(film, "scrapethissite.com/ajax")
            save_to_mongo(record["data"], record["source"], {
                "type": "dynamic_api",
                "extracted_at": record["extracted_at"]
            })
    except Exception as e:
        logging.error(f"Dynamic scraping error: {e}")

    try:
        logging.info("Starting OCR Processing...")
        img_path = "../../data/raw/images/test.png"
        if os.path.exists(img_path):
            raw_text, processed_text = compare_ocr(img_path)
            save_to_mongo(
                {"raw": raw_text, "processed": processed_text},
                "OCR Image",
                {"file_name": "test.png", "type": "image_ocr"}
            )

        scanned_pdf = "../../data/raw/scanned/sample.pdf"
        if os.path.exists(scanned_pdf):
            pdf_texts = ocr_scanned_pdf(scanned_pdf)
            for page_num, text in pdf_texts.items():
                record = build_ocr_record(text, "sample.pdf", page_number=page_num)
                save_to_mongo(record["data"], record["source"], {
                    "type": record["type"],
                    "page_number": record["page_number"],
                    "extracted_at": record["extracted_at"]
                })
        logging.info("OCR Processing finished.")
    except Exception as e:
        logging.error(f"OCR Error: {e}")

    logging.info("--- PIPELINE FINISHED SUCCESSFULLY ---")

if __name__ == "__main__":
    run_pipeline()