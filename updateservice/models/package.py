from datetime import datetime

from sqlalchemy import TIMESTAMP, VARCHAR, Column, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship

from updateservice.connection_db import Base


class Package(Base):
    __tablename__ = "packages"
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"))
    version = Column(String, nullable=False)
    description = Column(VARCHAR(255), nullable=True)
    file = Column(VARCHAR(255), nullable=True)
    url = Column(VARCHAR(1000), unique=True, nullable=True)
    hash = Column(VARCHAR(255), nullable=True)
    size = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    updated_at = Column(
        TIMESTAMP, default=datetime.utcnow(), onupdate=datetime.utcnow()
    )

    application = relationship("Application", backref=backref("packages"))

    __mapper_args__ = {"confirm_deleted_rows": False}
