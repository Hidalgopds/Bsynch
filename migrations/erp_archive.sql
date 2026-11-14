-- ERP: archive instead of delete (issues, supplier receipts, inventory items, suppliers,
-- unit materials, project units, material requests, attendance, contacts; daily_log wipe -> daily_log_archive).
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

-- Second batch: suppliers, unit materials, project units, material requests
alter table if exists public.suppliers         add column if not exists archived_at    timestamptz;
alter table if exists public.suppliers         add column if not exists archived_by    text;
alter table if exists public.suppliers         add column if not exists archive_reason text;

alter table if exists public.unit_materials    add column if not exists archived_at    timestamptz;
alter table if exists public.unit_materials    add column if not exists archived_by    text;
alter table if exists public.unit_materials    add column if not exists archive_reason text;

alter table if exists public.project_units     add column if not exists archived_at    timestamptz;
alter table if exists public.project_units     add column if not exists archived_by    text;
alter table if exists public.project_units     add column if not exists archive_reason text;

alter table if exists public.material_requests add column if not exists archived_at    timestamptz;
alter table if exists public.material_requests add column if not exists archived_by    text;
alter table if exists public.material_requests add column if not exists archive_reason text;
-- true when archiving a Delivered request put its quantities back in stock (restoring takes them out again)
alter table if exists public.material_requests add column if not exists stock_returned boolean not null default false;

-- Third batch: attendance reports and contacts
alter table if exists public.attendance_reports add column if not exists archived_at    timestamptz;
alter table if exists public.attendance_reports add column if not exists archived_by    text;
alter table if exists public.attendance_reports add column if not exists archive_reason text;

alter table if exists public.contacts           add column if not exists archived_at    timestamptz;
alter table if exists public.contacts           add column if not exists archived_by    text;
alter table if exists public.contacts           add column if not exists archive_reason text;

-- /admin/wipe no longer deletes: it moves every daily_log row here first (whole row as JSON)
create table if not exists public.daily_log_archive (
  id          bigserial primary key,
  original_id text,
  data        jsonb not null,
  archived_at timestamptz not null default now(),
  archived_by text
);
alter table public.daily_log_archive enable row level security;
create index if not exists daily_log_archive_original_id_idx on public.daily_log_archive (original_id);

-- Archived lists are read by archived_at
create index if not exists attendance_reports_archived_at_idx on public.attendance_reports (archived_at);
create index if not exists contacts_archived_at_idx           on public.contacts (archived_at);
create index if not exists unit_issues_archived_at_idx       on public.unit_issues (archived_at);
create index if not exists facturas_archived_at_idx          on public.facturas (archived_at);
create index if not exists inventory_items_archived_at_idx   on public.inventory_items (archived_at);
create index if not exists suppliers_archived_at_idx         on public.suppliers (archived_at);
create index if not exists unit_materials_archived_at_idx    on public.unit_materials (archived_at);
create index if not exists project_units_archived_at_idx     on public.project_units (archived_at);
create index if not exists material_requests_archived_at_idx on public.material_requests (archived_at);
