from datetime import datetime

from sqlalchemy import TIMESTAMP, VARCHAR, Column, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship

from updateservice.connection_db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(VARCHAR(255), unique=True, nullable=False)
    full_name = Column(VARCHAR(255), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    updated_at = Column(TIMESTAMP, default=datetime.now(), onupdate=datetime.now())
    last_login = Column(TIMESTAMP, default=datetime.now(), onupdate=datetime.now())


class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), unique=True, nullable=False)
    description = Column(VARCHAR(255), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    updated_at = Column(TIMESTAMP, default=datetime.now(), onupdate=datetime.now())

    def to_dict():
        return {"name": Team.name, "description": Team.description}


class UserTeams(Base):
    __tablename__ = "users_teams"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    updated_at = Column(TIMESTAMP, default=datetime.now(), onupdate=datetime.now())

    user = relationship("User", backref=backref("users_teams"))
    team = relationship("Team", backref=backref("users_teams"))
