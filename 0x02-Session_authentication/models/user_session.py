#!/usr/bin/env python3
""" UserSession module
"""
from models.base import Base
from datetime import datetime
from sqlalchemy import Column, String, DateTime

class UserSession(Base):
    """ UserSession class
    """
    __tablename__ = 'user_sessions'

    user_id = Column(String(128), nullable=False)
    session_id = Column(String(128), primary_key=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, user_id: str = None, session_id: str = None):
        """ Constructor
        """
        super().__init__()
        self.user_id = user_id
        self.session_id = session_id
