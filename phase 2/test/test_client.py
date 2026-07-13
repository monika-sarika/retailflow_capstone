import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from s3_ingest.client import S3ClientWrapper

def test_s3_client_initialization():
    """Ensure the client initializes with a boto3 session."""
    client = S3ClientWrapper()
    assert client.client is not None

@patch("boto3.Session")
def test_upload_file_success(mock_session, tmp_path):
    """Simulate a successful upload with a dummy file."""
    # Mock boto3 client
    mock_client = MagicMock()
    mock_session.return_value.client.return_value = mock_client

    # Create a temporary file
    test_file = tmp_path / "dummy.json"
    test_file.write_text("{}")

    client = S3ClientWrapper()
    result = client.upload_file(str(test_file), "retailflow-bucket", "raw/test.json")

    assert result is True
    mock_client.upload_file.assert_called_once_with(str(test_file), "retailflow-bucket", "raw/test.json")

@patch("boto3.Session")
def test_upload_file_missing(mock_session):
    """Ensure FileNotFoundError is raised when file does not exist."""
    mock_client = MagicMock()
    mock_session.return_value.client.return_value = mock_client

    client = S3ClientWrapper()
    with pytest.raises(FileNotFoundError):
        client.upload_file("nonexistent.json", "retailflow-bucket", "raw/test.json")
