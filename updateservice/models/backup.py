from sqlalchemy import TIMESTAMP, VARCHAR, Column, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship
from updateservice.connection_db import Base

class Backup(Base):
    __tablename__ = "backups"
    id = Column(Integer, primary_key=True)
    package_id = Column(Integer, unique=True)
    backup_path= Column(VARCHAR(255))