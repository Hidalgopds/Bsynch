-- ERP Home lists the companies that use the ERP (owner's request, 2026-11-21): TDG and MBR (Test).
-- Idempotent. Main project only. Nothing is deleted.

-- MBR (Test): a test ERP company (never billed). Paused until the ERP screens filter by company.
insert into public.contractor_companies (slug, name, status, hubs, billing_exempt, billing_status, is_demo, created_by, review_note)
values ('mbr', 'MBR (Test)', 'paused', '["erp"]'::jsonb, true, 'none', true, 'migration',
        'Test ERP company. Opens when the ERP separates companies (ERP step 2).')
on conflict (slug) do nothing;

-- The earlier ERP demo is replaced by MBR (Test): kept, but no longer listed in any hub.
update public.contractor_companies
   set hubs = '[]'::jsonb, review_note = 'Replaced by MBR (Test) on 2026-11-21 (owner asked for TDG and MBR only).'
 where slug = 'demo-erp' and hubs <> '[]'::jsonb;
