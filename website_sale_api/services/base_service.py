"""Base service for common functionalities across services."""

# pylint:disable=import-error
import base64
from typing import Any, Dict

from odoo.exceptions import ValidationError
from odoo.http import request


class BaseService:
    """Base service with common CRUD operations."""

    def __init__(self, env=None):
        self.env = env or request.env
        self.model_name = None
        self.default_domain = []
        self.fields = []

    def _get_model(self):
        """Get the model instance."""
        return self.env[self.model_name].sudo()

    def _get_current_website(self):
        """
        Fetch current website (INTERNAL CLASS METHOD)
        - Only called internally by _get_website_id
        - Not intended for external use
        """
        domain = f"{request.httprequest.scheme}://{request.httprequest.host}"
        website = (
            request.env["website"].sudo().search([("domain", "=", domain)], limit=1)
        )

        return website or request.env["website"].sudo().search(
            [], limit=1, order="id asc"
        )

    def _get_price_list(self, website):
        return website.pricelist_ids[0]

    def _get_base_url(self):
        """Return current base url."""
        return request.httprequest.host_url.rstrip("/")

    def _get_image_url(self, model, record_id, size="image_256"):
        """Get image URL for a specific model and record."""
        return f"{self._get_base_url()}/web/image/{model}/{record_id}/{size}"

    def search_count(self):
        """Get total count of records matching the domain."""
        return self._get_model().search_count(self.default_domain)

    def search_read(self, limit=None, offset=None, order=None):
        """Search and read records with given parameters."""
        return self._get_model().search_read(
            self.default_domain, self.fields, limit=limit, offset=offset, order=order
        )

    def get_record_by_id(self, record_id):
        """Get a single record by ID."""
        self.default_domain.append(("id", "=", record_id))
        records = self.search_read(limit=1)
        return records[0] if records else None

    def _create(self, data: Dict[str, Any]):
        """Create a new record."""
        if not data:
            raise ValidationError("No data provided for creation")
        try:
            return self._get_model().create(data)
        except Exception as e:
            raise ValidationError(f"Failed to create record: {str(e)}") from e

    def _write(self, record, data: Dict[str, Any]) -> bool:
        """Update a record."""
        if not data:
            return True
        try:
            record.write(data)
            return True
        except Exception as e:
            raise ValidationError(f"Failed to update record: {str(e)}") from e

    def _delete(self, record) -> bool:
        """Delete a record."""
        try:
            record.unlink()
            return True
        except Exception as e:
            raise ValidationError(f"Failed to delete record: {str(e)}") from e

    def _validate_image(self, file, max_size_mb: int = 5) -> bytes:
        """
        Validate image file.

        Args:
            file: File object from request
            max_size_mb: Maximum file size in MB

        Returns:
            bytes: Validated image data

        Raises:
            ValidationError: If validation fails
        """
        if not file:
            raise ValidationError("No image uploaded")

        if not file.mimetype or not file.mimetype.startswith("image/"):
            raise ValidationError("Invalid image file")

        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.mimetype not in allowed_types:
            raise ValidationError("Only JPEG, PNG, GIF, WEBP images are allowed")

        file_data = file.read()
        if len(file_data) > max_size_mb * 1024 * 1024:
            raise ValidationError(f"Image must be smaller than {max_size_mb}MB")

        return file_data

    def _encode_image(self, file_data: bytes) -> str:
        """
        Encode image data to base64 string.

        Args:
            file_data: Raw image data

        Returns:
            str: Base64 encoded image string
        """
        return base64.b64encode(file_data).decode("utf-8")

    def _upload_image(
        self,
        record,  # Changed from record_id to record
        file,
        max_size_mb: int = 5,
        field: str = "image_1920",
    ) -> str:
        """
        Upload and process image for a record.

        Args:
            record: Record object to update
            file: File object from request
            max_size_mb: Maximum file size in MB
            field: Field name to store image

        Returns:
            str: Base64 encoded image string
        """
        # Validate and read image
        file_data = self._validate_image(file, max_size_mb)

        # Encode to base64
        image_base64 = self._encode_image(file_data)

        # Update the record
        self._write(record, {field: image_base64})

        return image_base64
