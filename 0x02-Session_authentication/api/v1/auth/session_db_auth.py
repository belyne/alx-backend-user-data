#!/usr/bin/env python3
""" SessionDBAuth module
"""
from api.v1.auth.session_exp_auth import SessionExpAuth
from models.user_session import UserSession
from os import getenv
from datetime import datetime, timedelta

class SessionDBAuth(SessionExpAuth):
    """ SessionDBAuth class
    """
    def create_session(self, user_id: str = None) -> str:
        """ Create a Session ID for a user ID and store it in the database
        """
        if user_id is None or type(user_id) is not str:
            return None

        session_id = super().create_session(user_id)

        if session_id:
            user_session = UserSession(user_id=user_id, session_id=session_id)
            user_session.save()

        return session_id

    def user_id_for_session_id(self, session_id: str = None) -> str:
        """ Retrieve a User ID based on a Session ID by querying the database
        """
        if session_id is None or type(session_id) is not str:
            return None

        user_id = super().user_id_for_session_id(session_id)

        if self.session_duration > 0:
            user_session = UserSession.get(session_id)
            if user_session and user_session.created_at + timedelta(seconds=self.session_duration) < datetime.now():
                return None

        return user_id

    def destroy_session(self, request=None):
        """ Delete the user session / logout from the database
        """
        if request is None:
            return False

        session_id = self.session_cookie(request)
        if session_id is not None:
            user_id = self.user_id_for_session_id(session_id)
            if user_id:
                user_session = UserSession.get(session_id)
                if user_session:
                    user_session.delete()
                return True

        return False
