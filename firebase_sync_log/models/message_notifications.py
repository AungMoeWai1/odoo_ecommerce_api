"""Approval Notifications Module"""

# pylint: disable=broad-exception-caught,import-error,too-few-public-methods,protected-access
import logging

from odoo import models

from .firebase import FirebaseConnector

_logger = logging.getLogger(__name__)


def _collect_device_tokens(user) -> list:
    """Collect device token(s) from an employee record.

    Supports a single `device_token` char field or a sequence field named
    `device_tokens` (list/one2many) containing tokens. Returns list of tokens.
    """
    tokens = []
    if not user:
        return tokens

    # Check for single token field
    if hasattr(user, "mobile_device_token") and user.mobile_device_token:
        tokens.append(str(user.mobile_device_token))

    # Check for multiple tokens field
    if hasattr(user, "mobile_device_tokens") and user.mobile_device_tokens:
        for token_record in user.mobile_device_tokens:
            if hasattr(token_record, "token") and token_record.token:
                tokens.append(str(token_record.token))
    return list(dict.fromkeys(tokens))  # deduplicate preserving order


def _send_notifications_for_user(
    user, title: str, body: str, log_id, file_name: str = None
) -> bool:
    """Send notification(s) to the user's device token(s) using FirebaseConnector.

    Returns True if at least one send was attempted (not necessarily delivered).
    """
    tokens = _collect_device_tokens(user)
    if not tokens:
        _logger.info(
            "No device tokens for user %s, skipping notification",
            getattr(user, "id", None),
        )
        return False
    try:
        connector = (
            FirebaseConnector(file_name=file_name) if file_name else FirebaseConnector()
        )
        with connector:
            ok = False
            for token in tokens:
                try:
                    sent = connector.send_notification(
                        title=title, message=body, device_token=token
                    )
                    ok = ok or bool(sent)
                except Exception:
                    _logger.exception(
                        "Failed to send notification to token for user %s",
                        getattr(user, "id", None),
                    )
                if ok:
                    update_notification_log_status(log_id)
            return ok
    except Exception:
        _logger.exception("Failed to initialize FirebaseConnector")
        return False


def send_message_notification(user, record, title, body):
    """Send notification(s) to the user's device token(s) using FirebaseConnector."""
    log_id = create_notification_log(record, user.id, title, body)
    return _send_notifications_for_user(user, title, body, log_id)


def create_notification_log(record: models.Model, receiver_id, title: str, body: str):
    """Create a notification log entry."""
    log = (
        record.env["message.notification.log"]
        .sudo()
        .create(
            {
                "receiver_id": receiver_id,
                "model_name": record._name,
                "record_id": record.id,
                "title": title or "",
                "body": body or "",
            }
        )
    )
    return log


def update_notification_log_status(log_record):
    """Update status of existing notification log"""
    if not log_record:
        return False

    log_record.sudo().write({"status": "success"})
    return True
