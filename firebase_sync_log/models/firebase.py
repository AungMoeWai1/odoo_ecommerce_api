"""Firebase Connector Module"""

# pylint: disable=broad-exception-caught
import logging
import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore, get_app, initialize_app, messaging

DEFAULT_FILE_NAME = "ecommerce_key.json"
DEFAULT_DIR = "firebase_sync_log/key"

_logger = logging.getLogger(__name__)


def get_file_path(file_name=DEFAULT_FILE_NAME):
    """Get default file path

    Args:
        file_name (str, optional): Name of the firebase key file. Defaults to DEFAULT_FILE_NAME.

    Returns:
        None
    """
    path = Path(os.path.dirname(__file__))
    return os.path.join(path.parent.parent.absolute(), DEFAULT_DIR, file_name)


class FirebaseConnector:
    """Firebase Connector Class"""

    def __init__(self, file_name: str = DEFAULT_FILE_NAME):
        self.service_account_key_path = get_file_path(file_name=file_name)
        self.db = None

    def connect(self):
        """Connect to Firebase using the service account key."""
        try:
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(self.service_account_key_path)
            initialize_app(cred)
            self.db = firestore.client()
            return True
        except Exception as e:
            # Log or handle the error appropriately
            _logger.error("Error initializing Firebase: %s", e)
            return False

    def disconnect(self):
        """Disconnect from Firebase."""
        try:
            # Close Firebase connection
            firebase_admin.delete_app(get_app())
            self.db = None
            return True
        except Exception as e:
            # Log or handle the error appropriately
            _logger.error("Error disconnecting from Firebase: %s", e)
            return False

    def __enter__(self):
        # Connect to Firebase when entering the context
        if not self.connect():
            raise RuntimeError("Failed to connect to Firebase")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Disconnect from Firebase when exiting the context
        self.disconnect()

    def send_notification(self, title: str, message: str, device_token: str) -> bool:
        """
        Send a notification to a device using Firebase Cloud Messaging.

        Args:
            title (str): Title of the notification.
            message (str): Body of the notification.
            device_token (str): Device token to send the notification to.

        Returns:
            bool: True if the notification was sent successfully, False otherwise.
        """
        try:
            # Create the message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=message,
                ),
                token=device_token,
            )

            # Send the message
            response = messaging.send(message)
            _logger.info("Successfully sent message: %s", response)
            return True
        except Exception as e:
            _logger.error("Error sending notification via Firebase: %s", e)
            return False
