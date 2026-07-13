import logging
from pathlib import Path
from s3_ingest.client import S3ClientWrapper

# Setup logging consistent with S3ClientWrapper
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("s3_ingest_main")

def main():
    BUCKET = "retailflow-bucket"
    DATE_FOLDER = "dt=2026-07-08"
    DATA_DIR = Path("notebooks")  # 👈 Folder containing your JSON files
    
    files = ["orders_day1.json", "clickstream_day1.json", "order_items_day1.json"]
    s3 = S3ClientWrapper()
    
    uploaded_count = 0
    missing_count = 0

    for file in files:
        path = DATA_DIR / file  # 👈 Look inside notebooks/
        if not path.exists():
            logger.warning(f"Local file missing: {path}")
            missing_count += 1
            continue
            
        folder_name = file.replace("_day1.json", "")
        s3_path = f"raw/{folder_name}/{DATE_FOLDER}/{file}"
        
        logger.info(f"Uploading {path} → {s3_path}")
        try:
            s3.upload_file(str(path), BUCKET, s3_path)
            uploaded_count += 1
            logger.info(f"Ingested successfully: {s3_path}\n")
        except Exception as e:
            logger.error(f"Failed to upload {file}: {e}")

    logger.info(f"Upload Summary: {uploaded_count} uploaded, {missing_count} missing")

if __name__ == "__main__":
    main()
