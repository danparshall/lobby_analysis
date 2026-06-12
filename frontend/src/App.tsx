import { useEffect, useState } from "react";
import type { Filing, Stats } from "./types";
import { fetchStats, listFilings, searchFilings } from "./api";
import { StatsBar } from "./components/StatsBar";
import { FilingsTable } from "./components/FilingsTable";
import { FilingDetail } from "./components/FilingDetail";

export function App() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [query, setQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [filings, setFilings] = useState<Filing[]>([]);
  const [selected, setSelected] = useState<Filing | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats()
      .then(setStats)
      .catch((e) => setError(String(e)));
  }, []);

  async function runLoad() {
    setLoading(true);
    setError(null);
    try {
      const trimmed = query.trim();
      const results = trimmed
        ? await searchFilings(trimmed)
        : await listFilings({ filer_role: roleFilter || undefined, limit: 50 });
      setFilings(results);
    } catch (e) {
      setError(String(e));
      setFilings([]);
    } finally {
      setLoading(false);
    }
  }

  // Initial load + reload when the role filter changes (search is submit-driven).
  useEffect(() => {
    runLoad();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [roleFilter]);

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    runLoad();
  }

  return (
    <div className="app">
      <header className="header">
        <h1>State Lobbying Disclosure Explorer</h1>
        <p className="subtitle">
          Search and browse lobbying filings extracted from state disclosure
          portals into a single normalized schema.
        </p>
      </header>

      <StatsBar stats={stats} />

      <form className="controls" onSubmit={onSubmit}>
        <input
          type="search"
          placeholder="Search by filer name (e.g. DoorDash)…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          aria-label="Filter by filer role"
        >
          <option value="">All roles</option>
          <option value="client">Client</option>
          <option value="lobbyist">Lobbyist</option>
          <option value="firm">Firm</option>
        </select>
        <button type="submit">Search</button>
      </form>

      {error && <p className="error">Error: {error}</p>}

      <div className="results-layout">
        <div className="results">
          {loading ? (
            <p className="empty">Loading…</p>
          ) : (
            <>
              <p className="result-count">{filings.length} result(s)</p>
              <FilingsTable
                filings={filings}
                onSelect={setSelected}
                selectedId={selected?.id}
              />
            </>
          )}
        </div>
        {selected && (
          <FilingDetail filing={selected} onClose={() => setSelected(null)} />
        )}
      </div>
    </div>
  );
}
