-- ERP becomes multi-company (step 1 of 2, by Settings). Idempotent. Main project only.
-- Nothing is deleted or moved: every existing ERP row is marked as TDG Energy Services (the owner's).
-- Step 2 (ERP conversation): every ERP route reads/writes only the caller's company; then the
-- temporary DEFAULT 'tdg' below is removed and the demo ERP company is switched to active.

-- 1) Demo flag on companies (demo companies are never billed)
alter table public.contractor_companies add column if not exists is_demo boolean not null default false;

-- 2) Companies: TDG (ERP, owner's own) and two demo companies to show the system
insert into public.contractor_companies (slug, name, status, hubs, billing_exempt, billing_status, is_demo, created_by, review_note)
values
  ('tdg', 'TDG Energy Services', 'active', '["erp"]'::jsonb, true, 'none', false, 'migration', 'Owner''s company'),
  ('demo-construction', 'Demo Construction Co', 'active', '["contractor"]'::jsonb, true, 'none', true, 'migration', 'Demo to show Contractor'),
  ('demo-erp', 'Demo Field Services', 'paused', '["erp"]'::jsonb, true, 'none', true, 'migration',
   'Demo to show ERP. Paused until ERP routes filter by company (otherwise it would see TDG data)')
on conflict (slug) do nothing;

-- 3) Company column on every ERP table; existing rows -> 'tdg'
do $$
declare t text;
begin
  foreach t in array array['workers','checkins','attendance_reports','safety_meetings','daily_log',
    'inventory_items','unit_issues','unit_issue_history','project_units','unit_materials','unit_material_history',
    'sent_units','material_requests','material_documents','purchase_orders','suppliers','facturas','contacts',
    'notifications','notification_reads','worker_locations','worker_location_history']
  loop
    if to_regclass('public.' || t) is not null then
      execute format('alter table public.%I add column if not exists company text', t);
      execute format('update public.%I set company = %L where company is null', t, 'tdg');
      -- temporary: rows written by today's ERP code land in TDG until step 2
      execute format('alter table public.%I alter column company set default %L', t, 'tdg');
      execute format('alter table public.%I alter column company set not null', t);
      execute format('create index if not exists %I on public.%I (company)', t || '_company_idx', t);
    end if;
  end loop;
end $$;
