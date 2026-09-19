const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000/api";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // ignore parse errors
    }
    throw new Error(detail);
  }

  return res.json();
}

export const api = {
  listConversations: () => request("/conversations"),
  createConversation: () => request("/conversations", { method: "POST" }),
  deleteConversation: (id) => request(`/conversations/${id}`, { method: "DELETE" }),
  getMessages: (id) => request(`/conversations/${id}/messages`),
  sendMessage: (conversationId, message) =>
    request("/chat", {
      method: "POST",
      body: JSON.stringify({ conversation_id: conversationId, message }),
    }),
};
