import os
from azure.storage.blob import BlobServiceClient, ContentSettings

class BlobService:
    def __init__(self):
        self.conn = os.getenv("BLOB_CONNECTION_STRING", "")
        self.container = os.getenv("BLOB_CONTAINER_NAME", "uploads")

        self.client = None
        self.container_client = None

        if self.conn:
            self.client = BlobServiceClient.from_connection_string(self.conn)
            self.container_client = self.client.get_container_client(self.container)
            try:
                self.container_client.get_container_properties()
            except Exception:
                self.container_client.create_container()

    def upload_image(self, blob_name: str, data: bytes, content_type: str) -> str:
        if not self.container_client:
            raise RuntimeError("Blob Storage is not configured. Set BLOB_CONNECTION_STRING and BLOB_CONTAINER_NAME.")

        blob_client = self.container_client.get_blob_client(blob_name)
        blob_client.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )
        return blob_client.url
