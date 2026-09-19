import OrderStatusCard from "./OrderStatusCard.jsx";
import EscalationNotice from "./EscalationNotice.jsx";

export default function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`flex max-w-[75%] flex-col ${isUser ? "items-end" : "items-start"}`}>
        <div
          className={`whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-panel ${
            isUser
              ? "rounded-br-md bg-signal text-white"
              : "rounded-bl-md bg-white text-ink-900"
          }`}
        >
          {message.content}
        </div>

        {message.order_info && <OrderStatusCard order={message.order_info} />}
        {message.escalated && <EscalationNotice ticketId={message.ticket_id} />}

        {message.sources && message.sources.length > 0 && (
          <p className="mt-1.5 px-1 text-xs text-ink-600">
            Based on: {message.sources.join(", ")}
          </p>
        )}
      </div>
    </div>
  );
}
