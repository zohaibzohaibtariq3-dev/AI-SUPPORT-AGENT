export default function Sidebar({
  conversations,
  activeId,
  onSelect,
  onNewChat,
  onDelete,
}) {
  return (
    <aside className="flex h-full w-72 shrink-0 flex-col bg-ink-900 text-paper-50">
      <div className="px-5 pt-6 pb-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-signal font-display text-sm font-bold text-white">
            TN
          </div>
          <span className="font-display text-base font-bold tracking-tight">
            TechNova Support
          </span>
        </div>
      </div>

      <div className="px-4">
        <button
          onClick={onNewChat}
          className="flex w-full items-center justify-center gap-2 rounded-lg border border-ink-600 bg-ink-800 py-2.5 text-sm font-medium text-paper-50 transition hover:bg-ink-700 active:scale-[0.99]"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 3.5v9M3.5 8h9" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
          </svg>
          New chat
        </button>
      </div>

      <div className="mt-6 flex-1 overflow-y-auto px-3 pb-4">
        <p className="px-2 pb-2 text-xs font-medium text-ink-600/80">Conversations</p>

        {conversations.length === 0 && (
          <p className="px-2 py-3 text-sm text-ink-600">
            No conversations yet. Start one above.
          </p>
        )}

        <ul className="flex flex-col gap-1">
          {conversations.map((c) => (
            <li key={c.id}>
              <button
                onClick={() => onSelect(c.id)}
                className={`group flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-left text-sm transition ${
                  c.id === activeId
                    ? "bg-signal/20 text-white"
                    : "text-ink-600 hover:bg-ink-800 hover:text-paper-100"
                }`}
              >
                <span className="truncate">{c.title || "New Conversation"}</span>
                <span
                  role="button"
                  tabIndex={-1}
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(c.id);
                  }}
                  className="ml-2 shrink-0 opacity-0 transition group-hover:opacity-100 hover:text-red-400"
                  aria-label="Delete conversation"
                >
                  <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                    <path
                      d="M3.5 4.5h9M6.5 4.5V3a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v1.5M6.5 7.5v4M9.5 7.5v4M4.5 4.5l.6 8a1 1 0 0 0 1 .9h3.8a1 1 0 0 0 1-.9l.6-8"
                      stroke="currentColor"
                      strokeWidth="1.3"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </span>
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div className="border-t border-ink-800 px-5 py-4 text-xs text-ink-600">
        AI Customer Support Agent — portfolio project
      </div>
    </aside>
  );
}
