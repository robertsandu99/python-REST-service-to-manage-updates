from datetime import datetime

from sqlalchemy import TIMESTAMP, VARCHAR, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship

from updateservice.connection_db import Base


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String)
    deleted = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    updated_at = Column(TIMESTAMP, default=datetime.now(), onupdate=datetime.now())

    user_relationship = relationship("User", backref=backref("tokens"))
