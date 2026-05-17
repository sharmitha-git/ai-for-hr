from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime

from database.connection import Base

from datetime import datetime


class ConversationMemory(Base):

    __tablename__ = "conversation_memory"

    id = Column(
        Integer,
        primary_key=True
    )

    session_id = Column(
        String
    )

    # Partition key: available_jobs | candidate_matching | governance | outreach
    memory_scope = Column(
        String
    )

    role = Column(
        String
    )

    message = Column(
        Text
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )