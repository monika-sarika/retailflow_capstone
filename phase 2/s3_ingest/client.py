import os
import logging
from pathlib import Path
from typing import List, Optional
import boto3
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log

# Load environment variables (for AWS credentials or profile)
load_dotenv()

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("s3_ingest")

class S3ClientWrapper:
    def __init__(self, profile_name: Optional[str] = None):
        profile = profile_name or os.getenv("AWS_PROFILE")
        if profile:
            self.session = boto3.Session(profile_name=profile)
            logger.info(f"Using AWS profile: {profile}")
        else:
            self.session = boto3.Session()
            logger.info("Using default AWS session")
        self.client = self.session.client("s3")
        self.logger = logger

    @retry(reraise=True, stop=stop_after_attempt(4),
           wait=wait_exponential(multiplier=1, min=2, max=10),
           before_sleep=before_sleep_log(logger, logging.WARNING))
    def upload_file(self, file_path: str, bucket: str, object_name: str) -> bool:
        path = Path(file_path)
        if not path.exists():
            self.logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"{file_path} does not exist")

        self.logger.info(f"Uploading {file_path} → s3://{bucket}/{object_name}")
        self.client.upload_file(str(path), bucket, object_name)
        self.logger.info(f"✅ Successfully uploaded {file_path}")
        return True
