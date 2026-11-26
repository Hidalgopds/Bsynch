-- Outside reviewer account (owner's request, 2026-11-25). APPLIED in production.
-- The owner's test sign-up "el maracucho" created the account "Grok". It moves to Demo Construction Co (is_demo)
-- as Manager, so it sees every hub with example companies only (see _demo_viewer_company in app.py) and never
-- real data. The sign-up is marked rejected (nothing deleted). Idempotent.
update public.app_users set contractor_company = 'demo-construction'
  where name = 'Grok' and contractor_company = 'el-maracucho';
insert into public.app_config (key, value, updated_at)
values ('contractor_roles_demo-construction', '{"Grok":"admin"}'::jsonb, now())
on conflict (key) do update set value = public.app_config.value || '{"Grok":"admin"}'::jsonb, updated_at = now();
update public.contractor_companies set status = 'rejected',
  review_note = 'Test sign-up by the owner; the account (Grok) was moved to Demo Construction Co as an outside reviewer (2026-11-25).'
  where slug = 'el-maracucho' and status = 'pending';
insert into public.audit_log (at, actor, action, target, detail, path)
select now(), 'Settings (owner request)', 'company.reviewer_moved', 'Grok',
  '{"from":"el-maracucho","to":"demo-construction","role":"admin"}'::jsonb, 'migration'
where not exists (select 1 from public.audit_log where action = 'company.reviewer_moved' and target = 'Grok');
