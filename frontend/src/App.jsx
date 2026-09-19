import { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import ChatWindow from "./components/ChatWindow.jsx";
import { api } from "./api.js";

let localId = -1; // temp negative ids for optimistic messages before server assigns real ones

export default function App() {
  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    refreshConversations();
  }, []);

  useEffect(() => {
    if (activeId) {
      loadMessages(activeId);
    } else {
      setMessages([]);
    }
  }, [activeId]);

  async function refreshConversations() {
    try {
      const data = await api.listConversations();
      setConversations(data);
    } catch (e) {
      setError(e.message);
    }
  }

  async function loadMessages(id) {
    try {
      const data = await api.getMessages(id);
      setMessages(data);
    } catch (e) {
      setError(e.message);
    }
  }

  function handleNewChat() {
    setActiveId(null);
    setMessages([]);
    setError(null);
  }

  async function handleDelete(id) {
    try {
      await api.deleteConversation(id);
      if (id === activeId) {
        setActiveId(null);
        setMessages([]);
      }
      refreshConversations();
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleSend(text) {
    setError(null);

    const optimisticUserMsg = {
      id: localId--,
      role: "user",
      content: text,
    };
    setMessages((prev) => [...prev, optimisticUserMsg]);
    setIsLoading(true);

    try {
      const res = await api.sendMessage(activeId, text);

      const assistantMsg = {
        id: localId--,
        role: "assistant",
        content: res.reply,
        order_info: res.order_info,
        escalated: res.escalated,
        ticket_id: res.ticket_id,
        sources: res.sources,
      };
      setMessages((prev) => [...prev, assistantMsg]);

      if (!activeId) {
        setActiveId(res.conversation_id);
      }
      refreshConversations();
    } catch (e) {
      setError(e.message);
      setMessages((prev) => [
        ...prev,
        {
          id: localId--,
          role: "assistant",
          content:
            "Sorry, something went wrong reaching the support agent. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={setActiveId}
        onNewChat={handleNewChat}
        onDelete={handleDelete}
      />
      <div className="flex flex-1 flex-col">
        {error && (
          <div className="border-b border-red-200 bg-red-50 px-6 py-2 text-sm text-red-700">
            {error}
          </div>
        )}
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          onSend={handleSend}
          hasConversation={!!activeId || messages.length > 0}
        />
      </div>
    </div>
  );
}
