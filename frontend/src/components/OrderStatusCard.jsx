const STATUS_STYLES = {
  Delivered: "text-moss bg-moss-light",
  Shipped: "text-signal-dark bg-signal-light",
  Processing: "text-amber bg-amber-light",
  Cancelled: "text-red-600 bg-red-50",
};

export default function OrderStatusCard({ order }) {
  const badgeClass = STATUS_STYLES[order.status] || "text-ink-700 bg-paper-200";

  return (
    <div className="mt-2 w-full max-w-sm rounded-xl border border-paper-200 bg-white p-4 shadow-panel">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-ink-600">
            Order #{order.order_number}
          </p>
          <p className="mt-0.5 font-display text-sm font-semibold text-ink-900">
            {order.item}
          </p>
        </div>
        <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${badgeClass}`}>
          {order.status}
        </span>
      </div>

      <div className="mt-3 space-y-1 border-t border-paper-100 pt-3 text-sm text-ink-700">
        {order.tracking_number && (
          <div className="flex justify-between">
            <span className="text-ink-600">Tracking number</span>
            <span className="font-medium">{order.tracking_number}</span>
          </div>
        )}
        {order.expected_delivery && (
          <div className="flex justify-between">
            <span className="text-ink-600">Expected delivery</span>
            <span className="font-medium">{order.expected_delivery}</span>
          </div>
        )}
      </div>
    </div>
  );
}
