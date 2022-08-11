from sqlalchemy import Column, Integer, String, ForeignKey, Float, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)
    email = Column(String)
    role = Column(Integer)

    gold = Column(Integer)
    silver = Column(Integer)
    bronze = Column(Integer)

    leagues = relationship('LeagueUser', back_populates="user")


class League(Base):
    __tablename__ = "leagues"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    season = Column(Integer)
    start_time = Column(Integer)
    duration = Column(Integer)
    reset = Column(Integer)

    users = relationship("LeagueUser", back_populates="league")

class LeagueUser(Base):
    __tablename__ = "league_users"
    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(Integer)

    user = relationship("User", back_populates="leagues")
    league = relationship("League", back_populates="users")

class LeagueData(Base):
    __tablename__ = "league_data"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    league_id = Column(Integer, ForeignKey("leagues.id"))
    day = Column(Integer)
    streak = Column(Integer)
    study_days = Column(Integer)
    reviews_today = Column(Integer)
    retention_today = Column(Float)
    minutes_today = Column(Integer)
    reviews_league = Column(Integer)
    retention_league = Column(Float)
    minutes_league = Column(Integer)
    xp_today = Column(Float)
    xp_league = Column(Float)
    timestamp = Column(Integer)