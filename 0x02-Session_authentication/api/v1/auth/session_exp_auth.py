from api.v1.auth.session_auth import SessionAuth
from models.user_session import UserSession
import os
from datetime import datetime, timedelta


class SessionExpAuth(SessionAuth):
    """
    Session authentication with session expiration
    based on UserSession stored in-memory.

    This class extends SessionAuth and provides additional
    functionality for handling session expiration.

    Attributes:
    - user_id_by_session_id (dict): A dictionary to store user_id
    and created_at information based on session_id.
    """

    user_id_by_session_id = {}

    def __init__(self):
        """
        Initialize SessionExpAuth.

        Calls the constructor of the parent class (SessionAuth).
        """
        super().__init__()

    def create_session(self, user_id=None):
        """
        Create a new session for the given user_id.

        Args:
        - user_id (str): User ID for which the session is created.

        Returns:
        - session_id (str): The newly generated session ID.
        """
        if user_id is None:
            return None

        # Generate a new session ID
        session_id = self.generate_session_id()

        # Store the UserSession instance in user_id_by_session_id
        created_at = datetime.utcnow()
        self.user_id_by_session_id[session_id] = {"user_id": user_id, "created_at": created_at}

        return session_id

    def user_id_for_session_id(self, session_id=None):
        """
        Retrieve the User ID associated with the given session ID.

        Args:
        - session_id (str): Session ID for which to retrieve the User ID.

        Returns:
        - user_id (str): User ID associated with the session ID,
        or None if not found or expired.
        """
        if session_id is None or session_id not in self.user_id_by_session_id:
            return None

        # Retrieve user_id and created_at from user_id_by_session_id
        user_info = self.user_id_by_session_id.get(session_id, None)
        if user_info is None:
            return None

        user_id, created_at = user_info.get("user_id"), user_info.get("created_at")

        # Check for session expiration
        if self.is_session_expired(created_at):
            return None

        return user_id

    def destroy_session(self, request=None):
        """
        Destroy the UserSession associated with the session
        ID extracted from the request.

        Args:
        - request: Request object containing the session ID in the cookie.
        """
        if request is None:
            return

        # Extract session_id from the request cookie
        session_id = self.session_id_from_request(request)

        # Remove the session entry from user_id_by_session_id
        if session_id in self.user_id_by_session_id:
            del self.user_id_by_session_id[session_id]

    def is_session_expired(self, created_at):
        """
        Check if the session is expired based on the created_at timestamp.

        Args:
        - created_at (datetime): Timestamp indicating
        when the session was created.

        Returns:
        - expired (bool): True if the session is expired,
        False otherwise.
        """
        if self.session_duration is not None and self.session_duration > 0:
            expiration_time = created_at + timedelta(seconds=self.session_duration)
            now = datetime.utcnow()
            return expiration_time < now

        return False

# Instantiate the auth class based on the environment variable
if os.getenv("AUTH_TYPE") == "session_exp_auth":
    auth = SessionExpAuth()
else:
    # Default to SessionAuth if AUTH_TYPE is not set or different
    auth = SessionAuth()
