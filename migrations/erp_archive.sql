-- ERP: archive instead of delete (issues, supplier receipts, inventory items).
-- Records are never deleted: "delete" in the app now sets archived_at / archived_by.
-- Idempotent: safe to run more than once. RLS stays on, no policies (only the server reads/writes).

alter table if exists public.unit_issues     add column if not exists archived_at    timestamptz;
alter table if exists public.unit_issues     add column if not exists archived_by    text;
alter table if exists public.unit_issues     add column if not exists archive_reason text;

alter table if exists public.facturas        add column if not exists archived_at    timestamptz;
alter table if exists public.facturas        add column if not exists archived_by    text;
alter table if exists public.facturas        add column if not exists archive_reason text;

alter table if exists public.inventory_items add column if not exists archived_at    timestamptz;
alter table if exists public.inventory_items add column if not exists archived_by    text;
alter table if exists public.inventory_items add column if not exists archive_reason text;

-- Archived lists are read by archived_at
create index if not exists unit_issues_archived_at_idx     on public.unit_issues (archived_at);
create index if not exists facturas_archived_at_idx        on public.facturas (archived_at);
create index if not exists inventory_items_archived_at_idx on public.inventory_items (archived_at);
