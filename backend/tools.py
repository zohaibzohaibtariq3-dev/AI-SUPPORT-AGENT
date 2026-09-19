"""
Tools the AI agent can invoke. These are plain Python functions backed by
the SQLite database. They are exposed to the Groq model as "function
calling" tools (see ai_agent.py for the JSON schema definitions).
"""

from typing import Optional
from sqlalchemy.orm import Session

from models import Order, Ticket


def get_order_status(db: Session, order_number: str) -> dict:
    """
    Look up an order by its order number.

    Returns a dict describing the order, or an error dict if not found.
    This is called by the AI agent, and its return value is fed back to the
    model as a tool result so it can explain the status in natural language.
    """
    order_number = str(order_number).strip().lstrip("#")
    order = db.query(Order).filter(Order.order_number == order_number).first()

    if order is None:
        return {"found": False, "error": f"No order found with number {order_number}."}

    return {
        "found": True,
        "order_number": order.order_number,
        "item": order.item,
        "status": order.status,
        "tracking_number": order.tracking_number,
        "order_date": order.order_date,
        "expected_delivery": order.expected_delivery,
        "total_amount": order.total_amount,
    }


def create_support_ticket(
    db: Session,
    conversation_id: int,
    reason: str,
    summary: str,
) -> dict:
    """
    Create a support ticket for human follow-up, and persist it to SQLite.
    """
    ticket = Ticket(
        conversation_id=conversation_id,
        reason=reason,
        summary=summary,
        status="open",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return {
        "ticket_id": ticket.id,
        "status": ticket.status,
        "reason": ticket.reason,
    }
