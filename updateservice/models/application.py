from datetime import datetime

from sqlalchemy import TIMESTAMP, VARCHAR, Column, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship

from updateservice.connection_db import Base


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    name = Column(VARCHAR(255), unique=True, nullable=False)
    description = Column(VARCHAR(255), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    updated_at = Column(TIMESTAMP, default=datetime.now(), onupdate=datetime.now())

    team = relationship("Team", backref=backref("applications"))
    groups = relationship(
        "Group", secondary="applications_groups", back_populates="applications"
    )
