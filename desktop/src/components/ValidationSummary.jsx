export function ValidationSummary({ validation }) {
  if (validation.ok) {
    return (
      <div id="validation-summary" className="validation-summary is-valid" role="status">
        El proyecto está listo para validar.
      </div>
    );
  }

  return (
    <div id="validation-summary" className="validation-summary is-invalid" role="alert">
      <strong>{validation.issues.length} project issue{validation.issues.length === 1 ? "" : "s"}</strong>
      <ul>
        {validation.issues.map((issue) => (
          <li key={`${issue.field}-${issue.message}`}>{issue.message}</li>
        ))}
      </ul>
    </div>
  );
}
