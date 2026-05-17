from sqlalchemy import (
    Column,
    Integer,
    Float,
    Text,
    TIMESTAMP
)

from database.connection import Base


class Application(Base):

    __tablename__ = "applications"

    id = Column(
        Integer,
        primary_key=True
    )

    candidate_id = Column(Integer)

    job_id = Column(Integer)

    semantic_score = Column(Float)

    keyword_score = Column(Float)

    final_score = Column(Float)

    confidence = Column(Text)

    governance_flag = Column(Text)

    application_status = Column(Text)

    confidence_score = Column(Float)

    created_at = Column(TIMESTAMP)
