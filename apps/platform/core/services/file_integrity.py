from __future__ import annotations

import hashlib


def sha256_storage_file(field_file) -> str:
    """Calculate SHA-256 from a Django FieldFile without loading it all in memory."""
    digest = hashlib.sha256()
    opened_here = False
    try:
        if getattr(field_file, "closed", True):
            field_file.open("rb")
            opened_here = True
        try:
            field_file.seek(0)
        except (AttributeError, OSError):
            pass
        while True:
            chunk = field_file.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        try:
            field_file.seek(0)
        except (AttributeError, OSError):
            pass
        return digest.hexdigest()
    finally:
        if opened_here:
            field_file.close()
