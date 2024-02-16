#!/usr/bin/env python3
""" Session Authentication
"""
from api.v1.auth.auth import Auth
from os import getenv
from datetime import datetime, timedelta

class SessionExpAuth(Auth):
    """ SessionExpAuth class
    """
    user_id_by_session_id = {}
    user_id_exp_date_by_session_id = {}

    def __init__(self):
        """ Constructor
        """
        self.session_duration = 0

        try:
            self.session_duration = int(getenv('SESSION_DURATION', 0))
        except ValueError:
            pass

        super().__init__()

    def create_session(self, user_id: str = None) -> str:
        """ Create a Session ID for a user ID
        """
        if user_id is None or type(user_id) is not str:
            return None

        session_id = super().create_session(user_id)

        if session_id:
            SessionExpAuth.user_id_by_session_id[session_id] = user_id
            if self.session_duration > 0:
                expiration_time = datetime.now() + timedelta(seconds=self.session_duration)
                SessionExpAuth.user_id_exp_date_by_session_id[session_id] = expiration_time

        return session_id

    def user_id_for_session_id(self, session_id: str = None) -> str:
        """ Retrieve a User ID based on a Session ID
        """
        if session_id is None or type(session_id) is not str:
            return None

        user_id = SessionExpAuth.user_id_by_session_id.get(session_id, None)

        if self.session_duration > 0:
            exp_date = SessionExpAuth.user_id_exp_date_by_session_id.get(session_id, None)
            if exp_date and exp_date < datetime.now():
                return None

        return user_id

    def destroy_session(self, request=None):
        """ Delete the user session / logout
        """
        if request is None:
            return False

        session_id = self.session_cookie(request)
        if session_id is not None:
            user_id = self.user_id_for_session_id(session_id)
            if user_id:
                del SessionExpAuth.user_id_by_session_id[session_id]
                if self.session_duration > 0:
                    del SessionExpAuth.user_id_exp_date_by_session_id[session_id]
                return True

        return False
