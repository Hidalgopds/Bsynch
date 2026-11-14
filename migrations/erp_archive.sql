-- ERP: archive instead of delete (issues, supplier receipts, inventory items, suppliers,
-- unit materials, project units, material requests).
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

-- Archived lists are read by archived_at
create index if not exists unit_issues_archived_at_idx       on public.unit_issues (archived_at);
create index if not exists facturas_archived_at_idx          on public.facturas (archived_at);
create index if not exists inventory_items_archived_at_idx   on public.inventory_items (archived_at);
create index if not exists suppliers_archived_at_idx         on public.suppliers (archived_at);
create index if not exists unit_materials_archived_at_idx    on public.unit_materials (archived_at);
create index if not exists project_units_archived_at_idx     on public.project_units (archived_at);
create index if not exists material_requests_archived_at_idx on public.material_requests (archived_at);
