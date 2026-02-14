from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String)
    language = Column(String)
    is_demo = Column(String, default="false") # Store if sent in demo mode
    created_at = Column(DateTime, default=datetime.utcnow)
    
    logs = relationship("MessageLog", back_populates="campaign")

class MessageLog(Base):
    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    phone = Column(String)
    status = Column(String) # sent, failed
    response = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="logs")
