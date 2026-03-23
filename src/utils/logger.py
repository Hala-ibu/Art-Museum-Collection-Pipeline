import logging
import os

log_file_path = os.path.join(os.path.dirname(__file__), '../../pipeline.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()           
    ]
)

logger = logging.getLogger(__name__)