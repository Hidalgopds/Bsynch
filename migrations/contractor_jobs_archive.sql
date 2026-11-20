-- Contractor: Completed folder for work orders.
-- A work order at 100% can be moved to "Completed" (archived_at set) and reactivated later.
-- Nothing is deleted. Safe to re-run.
alter table contractor_jobs add column if not exists archived_at timestamptz;
alter table contractor_jobs add column if not exists archived_by text;
alter table contractor_jobs enable row level security;
