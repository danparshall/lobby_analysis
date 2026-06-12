import type { Filing } from "../types";
import { filerName } from "../types";
import { usd, titleCase } from "../format";

export function FilingsTable({
  filings,
  onSelect,
  selectedId,
}: {
  filings: Filing[];
  onSelect: (f: Filing) => void;
  selectedId?: string;
}) {
  if (filings.length === 0) {
    return <p className="empty">No filings match.</p>;
  }

  return (
    <table className="filings">
      <thead>
        <tr>
          <th>Filer</th>
          <th>Role</th>
          <th>State</th>
          <th>Type</th>
          <th className="num">Expenditure</th>
          <th>Period</th>
        </tr>
      </thead>
      <tbody>
        {filings.map((f) => (
          <tr
            key={f.id}
            onClick={() => onSelect(f)}
            className={f.id === selectedId ? "selected" : ""}
          >
            <td className="filer">{filerName(f)}</td>
            <td>{titleCase(f.filer_role)}</td>
            <td>{f.state}</td>
            <td>{titleCase(f.filing_type)}</td>
            <td className="num">{usd(f.total_expenditure)}</td>
            <td className="period">
              {f.reporting_period_start ?? "—"}
              {f.reporting_period_end ? ` – ${f.reporting_period_end}` : ""}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
