// Subset of the backend LobbyingFiling shape the UI reads.
// Mirrors src/lobby_analysis/models/filings.py (only the fields we display).

export interface NamedEntity {
  id: string;
  name: string;
}

export interface BillReference {
  identifier?: string | null;
  title?: string | null;
}

export interface LobbyingPosition {
  bill_reference?: BillReference | null;
  position?: string | null;
  general_issue_area?: string | null;
  description?: string | null;
}

export interface LobbyingExpenditure {
  category: string;
  amount?: number | null;
  recipient_name?: string | null;
  purpose?: string | null;
}

export interface Filing {
  id: string;
  state: string;
  filing_id?: string | null;
  filing_type: string;
  filer_role: string;
  filer_person?: NamedEntity | null;
  filer_organization?: NamedEntity | null;
  reporting_period_start?: string | null;
  reporting_period_end?: string | null;
  filed_date?: string | null;
  total_expenditure?: number | null;
  total_compensation?: number | null;
  total_income?: number | null;
  total_hours_communicating?: number | null;
  source_url?: string | null;
  positions: LobbyingPosition[];
  expenditures: LobbyingExpenditure[];
}

export interface Stats {
  total: number;
  by_state: Record<string, number>;
  by_filer_role: Record<string, number>;
  top_spenders: { name: string; total_expenditure: number }[];
}

export function filerName(f: Filing): string {
  return f.filer_person?.name ?? f.filer_organization?.name ?? "(unnamed)";
}
