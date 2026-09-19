"""
ORM models (SQLAlchemy) and API schemas (Pydantic) for the support agent.
"""

import datetime
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from database import Base


# --------------------------------------------------------------------------
# SQLAlchemy ORM models
# --------------------------------------------------------------------------

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)  # e.g. "1005"
    customer_name = Column(String)
    item = Column(String)
    status = Column(String)  # e.g. "Processing", "Shipped", "Delivered", "Cancelled"
    tracking_number = Column(String, nullable=True)
    total_amount = Column(Float)
    order_date = Column(String)
    expected_delivery = Column(String, nullable=True)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String)  # "user" | "assistant" | "system"
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    reason = Column(String)
    summary = Column(Text)
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# --------------------------------------------------------------------------
# Pydantic schemas (API request/response bodies)
# --------------------------------------------------------------------------

class ConversationOut(BaseModel):
    id: int
    title: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str


class OrderInfo(BaseModel):
    order_number: str
    status: str
    item: str
    tracking_number: Optional[str] = None
    expected_delivery: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: int
    reply: str
    order_info: Optional[OrderInfo] = None
    escalated: bool = False
    ticket_id: Optional[int] = None
    sources: List[str] = []
