export default function EscalationNotice({ ticketId }) {
  return (
    <div className="mt-2 flex w-full max-w-sm items-start gap-3 rounded-xl border border-amber/30 bg-amber-light px-4 py-3">
      <svg width="18" height="18" viewBox="0 0 16 16" fill="none" className="mt-0.5 shrink-0 text-amber">
        <path
          d="M8 5.5v3M8 10.8h.01M7.15 2.5 1.8 12a1 1 0 0 0 .87 1.5h10.66a1 1 0 0 0 .87-1.5L8.85 2.5a1 1 0 0 0-1.7 0Z"
          stroke="currentColor"
          strokeWidth="1.3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <div>
        <p className="text-sm font-medium text-ink-900">Forwarded to support</p>
        <p className="mt-0.5 text-sm text-ink-700">
          {ticketId
            ? `A human agent will follow up shortly (ticket #${ticketId}).`
            : "A human agent will follow up shortly."}
        </p>
      </div>
    </div>
  );
}
