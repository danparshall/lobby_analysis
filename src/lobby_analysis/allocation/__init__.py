"""Allocation-matrix inference + chain composition across state lobbying
disclosure releases.

Per-state subpackages (e.g. ``allocation.wi``) consume the upstream
release TSVs and produce per-(lobbyist, principal, semester) hour
matrices via bipartite matrix completion (IPF / RAS), then compose those
matrices with bill-effort + sponsorship metadata into the end-to-end
{principal, lobbyist, lawmaker, bill} influence chain.
"""
