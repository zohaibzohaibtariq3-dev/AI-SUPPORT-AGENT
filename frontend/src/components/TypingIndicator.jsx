export default function TypingIndicator() {
  return (
    <div className="flex items-center gap-1.5 rounded-2xl bg-white px-4 py-3 shadow-panel">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="h-1.5 w-1.5 animate-bounce rounded-full bg-ink-600"
          style={{ animationDelay: `${i * 0.12}s` }}
        />
      ))}
    </div>
  );
}
