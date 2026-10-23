"""Campaign file storage helpers (local MEDIA_ROOT in dev; swap for R2/S3 later)."""

import hashlib
import os
import re
import uuid

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from ..models import CampaignFile


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def clean_filename(name):
    """Sanitize a filename to a safe basename (port of the MVP's cleanFilename)."""
    name = os.path.basename(str(name or ""))
    name = re.sub(r"[^\w.\- ]", "_", name).strip()
    return (name or "file")[:200]


def store_campaign_file(campaign, uploaded_file, role, user):
    """Persist an uploaded file and its metadata record.

    Returns the created ``CampaignFile``.
    """
    data = uploaded_file.read()
    name = clean_filename(uploaded_file.name)
    content_type = getattr(uploaded_file, "content_type", "") or "application/octet-stream"
    checksum = sha256_hex(data)
    key = f"campaigns/{campaign.owner_id}/{campaign.id}/{uuid.uuid4().hex}-{name}"
    saved_path = default_storage.save(key, ContentFile(data))
    return CampaignFile.objects.create(
        campaign=campaign,
        file_role=role,
        original_filename=name,
        content_type=content_type,
        size_bytes=len(data),
        storage_key=saved_path,
        checksum=checksum,
        uploaded_by=user,
    )


def read_campaign_file(campaign_file):
    """Return the file bytes for a stored CampaignFile."""
    with default_storage.open(campaign_file.storage_key, "rb") as fh:
        return fh.read()


def delete_campaign_file(campaign_file):
    """Delete the backing file and its record."""
    default_storage.delete(campaign_file.storage_key)
    campaign_file.delete()
