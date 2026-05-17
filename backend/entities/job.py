from sqlalchemy import (
    Column,
    Integer,
    String,
    Text
)

from database.connection import Base


class Job(Base):

    __tablename__ = "jobs"

    id = Column(
        Integer,
        primary_key=True
    )

    title = Column(String)

    description = Column(Text)

    required_skills = Column(Text)