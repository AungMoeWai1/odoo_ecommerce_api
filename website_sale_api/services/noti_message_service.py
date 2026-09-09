"""Message Notification Service."""

# pylint:disable=broad-exception-caught
from typing import Any, Dict

from ..schemas.noti_message_schema import NotificationData, NotificationResponse
from .pagination_service import PaginationService


class NotiMessageService(PaginationService):
    """Notification Service to get and update notification logs."""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "message.notification.log"
        self.fields = [
            "id",
            "name",
            "receiver_id",
            "read_status",
            "status",
            "create_date",
            "title",
            "body",
        ]
        self.default_sort = "id"

    def get_noti_list(self, user, kwargs: Dict[str, Any]):
        """Retrieve a list of notification message with pagination."""
        self.default_domain = [("receiver_id", "=", user.id)]
        paginated = self.get_paginated_from_kwargs(kwargs)

        return NotificationResponse(
            data=[self._format_messages(message) for message in paginated["data"]],
            total=paginated["total"],
            total_pages=paginated["total_pages"],
            page=paginated["page"],
            size=paginated["size"],
            has_prev=paginated["has_prev"],
            has_next=paginated["has_next"],
        )

    def _format_messages(self, message: Dict) -> NotificationData:
        """Convert message data to NotificationData schema."""

        return NotificationData(
            id=message["id"],
            name=message["name"],
            receiver_id=message["receiver_id"][0] if message["receiver_id"] else None,
            receiver_name=message["receiver_id"][1] if message["receiver_id"] else None,
            read_status=message["read_status"],
            status=message["status"],
            create_date=message["create_date"],
            title=message.get("title"),
            body=message.get("body"),
        )

    def bulk_mark_as_read(self, ids: list[int]) -> bool:
        """Bulk update read status of notification logs to 'read'"""
        try:
            if not ids:
                return False

            records = self._get_model().browse(ids)

            return bool(records and records.write({"read_status": "read"}))

        except Exception:
            return False
