from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    TIMESTAMP
)

from database.connection import Base

class Candidate(Base):

    __tablename__ = "candidates"

    id = Column(
        Integer,
        primary_key=True
    )

    full_name = Column(String)

    email = Column(String)

    phone = Column(String)

    resume_filename = Column(String)

    original_resume = Column(Text)

    masked_resume = Column(Text)

    skills = Column(Text)

    created_at = Column(TIMESTAMP)
