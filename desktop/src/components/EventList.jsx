export function EventList({ events }) {
  return (
    <ol id="event-list" className="event-list" aria-live="polite">
      {events.map((event, index) => (
        <li key={`${event.type}-${event.stage}-${index}`}>
          <span className="event-type">{event.type}</span>
          <span className="event-stage">
            {event.stage}: {event.message}
          </span>
          <span className="event-progress">{event.total ? `${event.current || 0}/${event.total}` : ""}</span>
        </li>
      ))}
    </ol>
  );
}
