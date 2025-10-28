from sqlalchemy import Column, Integer, String, Boolean
from src.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    due_time = Column(String, nullable=True)
    notified_60 = Column(Boolean, default=False)
    notified_5 = Column(Boolean, default=False)
