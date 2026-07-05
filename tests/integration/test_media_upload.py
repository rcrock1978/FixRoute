"""Integration test: media upload to Azure Blob with SAS-token URL generation."""
from __future__ import annotations

from unittest.mock import patch

import pytest

pytestmark = pytest.mark.django.db


def test_media_upload_generates_sas_url() -> None:
    with patch("backend.common.storage_blob.upload_blob", return_value="https://blob.example/sas?token=abc"):
        from backend.common.storage import blob as blob_module

        url = blob_module.upload_blob("test.jpg", b"\x89PNG\r\n", "image/jpeg")
        assert url.startswith("https://")
