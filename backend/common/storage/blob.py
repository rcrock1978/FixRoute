"""Azure Blob Storage client — SAS-token URL generation for media access per FR-015.

Hot → Cool → Archive lifecycle is configured via Terraform (see infra/terraform/blob_lifecycle.tf).
Soft-delete + immutable blob policy enforce the 30-day erasure SLA.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from azure.storage.blob import BlobClient, BlobSasPermissions, generate_blob_sas

logger = logging.getLogger(__name__)


def get_blob_client(blob_name: str) -> "BlobClient":
    """Return a BlobClient for a path inside the configured container."""
    from azure.storage.blob import BlobClient

    return BlobClient(
        account_url=settings.AZURE_BLOB_ACCOUNT_URL,
        container_name=settings.AZURE_BLOB_CONTAINER,
        blob_name=blob_name,
    )


def generate_sas_url(blob_name: str, ttl_seconds: int | None = None) -> str:
    """Generate a short-lived SAS URL scoped to a single blob.

    Per FR-015: SAS tokens are scoped per-request to enforce tenant isolation.
    """
    from azure.storage.blob import generate_blob_sas, BlobSasPermissions

    ttl = ttl_seconds or settings.AZURE_BLOB_SAS_TTL_SECONDS
    sas_token = generate_blob_sas(
        account_name=settings.AZURE_BLOB_ACCOUNT_URL.split("//")[1].split(".")[0],
        container_name=settings.AZURE_BLOB_CONTAINER,
        blob_name=blob_name,
        account_key=settings.AZURE_BLOB_ACCOUNT_KEY,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(timezone.utc) + timedelta(seconds=ttl),
    )
    return f"{settings.AZURE_BLOB_ACCOUNT_URL}/{settings.AZURE_BLOB_CONTAINER}/{blob_name}?{sas_token}"


def upload_blob(blob_name: str, data: bytes, content_type: str) -> str:
    """Upload a blob and return the SAS URL for read access."""
    client = get_blob_client(blob_name)
    client.upload_blob(data, overwrite=True, content_settings={"content_type": content_type})
    logger.info("blob.uploaded", extra={"blob": blob_name, "bytes": len(data)})
    return generate_sas_url(blob_name)


def soft_delete_blob(blob_name: str) -> None:
    """Mark a blob for soft-delete (Azure Blob soft-delete policy retains it for N days)."""
    client = get_blob_client(blob_name)
    client.soft_delete_blob()
    logger.info("blob.soft_deleted", extra={"blob": blob_name})
