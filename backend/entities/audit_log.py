from sqlalchemy import (
    Column,
    Integer,
    Text,
    TIMESTAMP
)

from database.connection import Base


class AuditLog(Base):

    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True
    )

    application_id = Column(Integer)

    action_type = Column(Text)

    action_details = Column(Text)

    created_at = Column(TIMESTAMP)
