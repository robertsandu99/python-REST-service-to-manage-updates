from datetime import datetime

from sqlalchemy import TIMESTAMP, VARCHAR, Column, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship

from updateservice.connection_db import Base


class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    updated_at = Column(
        TIMESTAMP, default=datetime.utcnow(), onupdate=datetime.utcnow()
    )
    applications = relationship(
        "Application", secondary="applications_groups", back_populates="groups"
    )


class ApplicationGroup(Base):
    __tablename__ = "applications_groups"
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    updated_at = Column(
        TIMESTAMP, default=datetime.utcnow(), onupdate=datetime.utcnow()
    )
