import type { Stats } from "../types";
import { usd, titleCase } from "../format";

export function StatsBar({ stats }: { stats: Stats | null }) {
  if (!stats) return null;

  const states = Object.entries(stats.by_state).sort((a, b) => b[1] - a[1]);
  const roles = Object.entries(stats.by_filer_role).sort((a, b) => b[1] - a[1]);

  return (
    <section className="stats">
      <div className="stat-cards">
        <div className="card">
          <div className="card-num">{stats.total.toLocaleString()}</div>
          <div className="card-label">Filings</div>
        </div>
        <div className="card">
          <div className="card-num">{states.length}</div>
          <div className="card-label">
            {states.length === 1 ? "State" : "States"}
          </div>
        </div>
        {roles.map(([role, n]) => (
          <div className="card" key={role}>
            <div className="card-num">{n.toLocaleString()}</div>
            <div className="card-label">{titleCase(role)}</div>
          </div>
        ))}
      </div>

      {stats.top_spenders.length > 0 && (
        <div className="top-spenders">
          <h3>Top spenders</h3>
          <ol>
            {stats.top_spenders.map((s) => (
              <li key={s.name}>
                <span className="spender-name">{s.name}</span>
                <span className="spender-amt">{usd(s.total_expenditure)}</span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </section>
  );
}
