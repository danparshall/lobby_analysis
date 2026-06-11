import type { Filing } from "../types";
import { filerName } from "../types";
import { usd, titleCase } from "../format";

export function FilingDetail({
  filing,
  onClose,
}: {
  filing: Filing;
  onClose: () => void;
}) {
  return (
    <aside className="detail">
      <div className="detail-head">
        <h2>{filerName(filing)}</h2>
        <button className="close" onClick={onClose} aria-label="Close">
          ×
        </button>
      </div>

      <dl className="detail-grid">
        <dt>State</dt>
        <dd>{filing.state}</dd>
        <dt>Role</dt>
        <dd>{titleCase(filing.filer_role)}</dd>
        <dt>Filing type</dt>
        <dd>{titleCase(filing.filing_type)}</dd>
        {filing.filing_id && (
          <>
            <dt>Native ID</dt>
            <dd>{filing.filing_id}</dd>
          </>
        )}
        <dt>Reporting period</dt>
        <dd>
          {filing.reporting_period_start ?? "—"}
          {filing.reporting_period_end ? ` – ${filing.reporting_period_end}` : ""}
        </dd>
        <dt>Total expenditure</dt>
        <dd>{usd(filing.total_expenditure)}</dd>
        {filing.total_compensation != null && (
          <>
            <dt>Compensation</dt>
            <dd>{usd(filing.total_compensation)}</dd>
          </>
        )}
        {filing.total_income != null && (
          <>
            <dt>Income</dt>
            <dd>{usd(filing.total_income)}</dd>
          </>
        )}
        {filing.total_hours_communicating != null && (
          <>
            <dt>Hours communicating</dt>
            <dd>{filing.total_hours_communicating}</dd>
          </>
        )}
      </dl>

      {filing.positions.length > 0 && (
        <section className="detail-section">
          <h3>Positions ({filing.positions.length})</h3>
          <ul>
            {filing.positions.map((p, i) => (
              <li key={i}>
                <strong>
                  {p.bill_reference?.identifier ??
                    p.general_issue_area ??
                    "(issue)"}
                </strong>
                {p.position ? ` — ${titleCase(p.position)}` : ""}
                {p.bill_reference?.title ? (
                  <div className="muted">{p.bill_reference.title}</div>
                ) : p.description ? (
                  <div className="muted">{p.description}</div>
                ) : null}
              </li>
            ))}
          </ul>
        </section>
      )}

      {filing.expenditures.length > 0 && (
        <section className="detail-section">
          <h3>Expenditures ({filing.expenditures.length})</h3>
          <ul>
            {filing.expenditures.map((e, i) => (
              <li key={i}>
                <span>{titleCase(e.category)}</span>
                {e.recipient_name ? ` → ${e.recipient_name}` : ""}
                <span className="exp-amt">{usd(e.amount)}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {filing.source_url && (
        <a className="source-link" href={filing.source_url} target="_blank" rel="noreferrer">
          View source filing ↗
        </a>
      )}
    </aside>
  );
}
