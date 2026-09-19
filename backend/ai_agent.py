"""
The core AI agent. Given a user message and conversation history, this:

  1. Retrieves relevant knowledge-base chunks via RAG (rag.py).
  2. Sends the conversation + retrieved context + tool definitions to Groq.
  3. If the model requests a tool call (order lookup / escalate to human),
     executes the corresponding Python function against SQLite and feeds
     the result back to the model for a final natural-language reply.
  4. Returns the final reply plus structured metadata (order info,
     escalation flag, ticket id, KB sources used) for the frontend to render.
"""

import os
import json
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from groq import Groq
from sqlalchemy.orm import Session

from rag import get_knowledge_base
from tools import get_order_status, create_support_ticket

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

_client: Optional[Groq] = None


def get_client() -> Groq:
    global _client
    if _client is None:
        if not GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


SYSTEM_PROMPT = """You are the customer support AI assistant for TechNova, an \
online electronics store.

Rules you must always follow:
1. For any question about company policy (shipping, refunds, cancellations, \
warranty, payments, exchanges), you MUST rely only on the "Knowledge base \
context" provided below in this conversation. Never invent or guess a policy \
detail. If the context does not contain the answer, say you're not sure and \
offer to escalate to a human agent.
2. If the customer asks about the status of a specific order (they will \
usually give an order number, e.g. "#1005" or "1005"), call the \
get_order_status tool with that order number instead of guessing.
3. If the customer explicitly asks to speak to a human/agent/person, or if \
you are unable to resolve their issue after a reasonable attempt, call the \
create_support_ticket tool to escalate, then let them know it's been \
forwarded to the support team.
4. Be concise, friendly, and professional. Do not mention tool names, \
function calls, or internal system details to the customer.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": (
                "Look up the current status of a customer's order by its "
                "order number. Use this whenever the customer asks where "
                "their order is or mentions an order number."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_number": {
                        "type": "string",
                        "description": "The order number, e.g. '1005' or '#1005'.",
                    }
                },
                "required": ["order_number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_support_ticket",
            "description": (
                "Create a support ticket to escalate the conversation to a "
                "human agent. Use this when the customer asks for a human, "
                "or when the issue cannot be resolved from the knowledge "
                "base or order lookup."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Short reason/category for the escalation.",
                    },
                    "summary": {
                        "type": "string",
                        "description": "A brief summary of the customer's issue for the human agent.",
                    },
                },
                "required": ["reason", "summary"],
            },
        },
    },
]


def _build_kb_context(user_message: str) -> (str, List[str]):
    kb = get_knowledge_base()
    results = kb.search(user_message, k=3)
    if not results:
        return "", []

    context_blocks = [chunk for chunk, _score in results]
    sources = []
    for chunk in context_blocks:
        first_line = chunk.splitlines()[0].replace("TITLE:", "").strip()
        sources.append(first_line)

    context_text = "\n\n---\n\n".join(context_blocks)
    return context_text, sources


def run_agent(
    db: Session,
    conversation_id: int,
    user_message: str,
    history: List[Dict[str, str]],
) -> Dict[str, Any]:
    """
    Run one turn of the agent.

    history: list of {"role": "user"|"assistant", "content": str} for prior
    turns in this conversation (most recent last), NOT including the new
    user_message.

    Returns a dict with keys: reply, order_info, escalated, ticket_id, sources.
    """
    client = get_client()

    kb_context, sources = _build_kb_context(user_message)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if kb_context:
        messages.append(
            {
                "role": "system",
                "content": f"Knowledge base context (use this for policy questions):\n\n{kb_context}",
            }
        )

    # Include recent history for conversational continuity (cap to last 10 turns).
    messages.extend(history[-10:])
    messages.append({"role": "user", "content": user_message})

    result = {
        "reply": "",
        "order_info": None,
        "escalated": False,
        "ticket_id": None,
        "sources": sources,
    }

    # First call: let the model decide whether to use a tool.
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.3,
        max_tokens=800,
    )

    choice = response.choices[0]
    assistant_msg = choice.message

    if assistant_msg.tool_calls:
        # Append the assistant's tool-call message to the running transcript.
        messages.append(
            {
                "role": "assistant",
                "content": assistant_msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in assistant_msg.tool_calls
                ],
            }
        )

        for tc in assistant_msg.tool_calls:
            fn_name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}

            if fn_name == "get_order_status":
                tool_result = get_order_status(db, args.get("order_number", ""))
                if tool_result.get("found"):
                    result["order_info"] = {
                        "order_number": tool_result["order_number"],
                        "status": tool_result["status"],
                        "item": tool_result["item"],
                        "tracking_number": tool_result.get("tracking_number"),
                        "expected_delivery": tool_result.get("expected_delivery"),
                    }

            elif fn_name == "create_support_ticket":
                tool_result = create_support_ticket(
                    db,
                    conversation_id=conversation_id,
                    reason=args.get("reason", "General inquiry"),
                    summary=args.get("summary", user_message),
                )
                result["escalated"] = True
                result["ticket_id"] = tool_result["ticket_id"]

            else:
                tool_result = {"error": f"Unknown tool {fn_name}"}

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": fn_name,
                    "content": json.dumps(tool_result),
                }
            )

        # Second call: model produces the final natural-language reply now
        # that it has the tool results.
        follow_up = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=800,
        )
        result["reply"] = follow_up.choices[0].message.content or ""
    else:
        result["reply"] = assistant_msg.content or ""

    return result
