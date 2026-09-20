"""
FastAPI application entry point for the AI Customer Support Agent.

Run with: uvicorn main:app --reload --port 8000
"""

from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db, init_db
from models import (
    Conversation,
    Message,
    ConversationOut,
    MessageOut,
    ChatRequest,
    ChatResponse,
    OrderInfo,
)
from ai_agent import run_agent


app = FastAPI(title="AI Customer Support Agent")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://ai-support-agent-rnuh.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/conversations", response_model=List[ConversationOut])
def list_conversations(db: Session = Depends(get_db)):
    conversations = (
        db.query(Conversation)
        .order_by(Conversation.created_at.desc())
        .all()
    )
    return conversations


@app.post("/api/conversations", response_model=ConversationOut)
def create_conversation(db: Session = Depends(get_db)):
    conversation = Conversation(title="New Conversation")
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@app.get(
    "/api/conversations/{conversation_id}/messages",
    response_model=List[MessageOut],
)
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    return messages


@app.delete("/api/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    db.delete(conversation)
    db.commit()

    return {"deleted": True}


def _make_title(text: str, max_len: int = 40) -> str:
    text = text.strip().replace("\n", " ")
    return text[:max_len] + ("..." if len(text) > max_len else "")


@app.post("/api/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
):
    if payload.conversation_id:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == payload.conversation_id)
            .first()
        )

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )
    else:
        conversation = Conversation(
            title=_make_title(payload.message)
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    existing_count = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .count()
    )

    if existing_count == 0:
        conversation.title = _make_title(payload.message)
        db.commit()

    prior_messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
        .all()
    )

    history = [
        {"role": m.role, "content": m.content}
        for m in prior_messages
    ]

    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=payload.message,
    )

    db.add(user_msg)
    db.commit()

    try:
        agent_result = run_agent(
            db=db,
            conversation_id=conversation.id,
            user_message=payload.message,
            history=history,
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    reply_text = (
        agent_result["reply"]
        or "Sorry, I couldn't generate a response."
    )

    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=reply_text,
    )

    db.add(assistant_msg)
    db.commit()

    order_info = None

    if agent_result.get("order_info"):
        order_info = OrderInfo(
            **agent_result["order_info"]
        )

    return ChatResponse(
        conversation_id=conversation.id,
        reply=reply_text,
        order_info=order_info,
        escalated=agent_result.get("escalated", False),
        ticket_id=agent_result.get("ticket_id"),
        sources=agent_result.get("sources", []),
    )


