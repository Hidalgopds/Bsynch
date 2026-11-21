-- Every company hub has an example company (owner's request, 2026-11-21). Family Hub excluded.
-- Contractor: demo-construction (exists). ERP: mbr "MBR (Test)" (exists). New: Marketing and Storefront.
-- Idempotent. Main project only. Demo companies are never billed.
insert into public.contractor_companies (slug, name, status, hubs, billing_exempt, billing_status, is_demo, created_by, review_note)
values
  ('demo-marketing', 'Demo Marketing Co', 'active', '["marketing"]'::jsonb, true, 'none', true, 'migration',
   'Example for the Marketing hub (screens for companies being built)'),
  ('demo-store', 'Demo Store', 'active', '["storefront"]'::jsonb, true, 'none', true, 'migration',
   'Example for the Storefront hub (being built)')
on conflict (slug) do nothing;
