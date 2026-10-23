-- Hicons go-live (2026-10-23): removes the test documents, keeps users, settings and Renee's
-- real Warranty work orders (WO-004..WO-010). Everything removed was first copied to
-- app_config 'hicons_test_backup_20261023' (photos only counted, not copied).
begin;
create temp table tj on commit drop as select (x->>'id')::uuid id from app_config, jsonb_array_elements(value->'jobs') x where key='hicons_test_backup_20261023';
create temp table ti on commit drop as select (x->>'id')::uuid id from app_config, jsonb_array_elements(value->'invoices') x where key='hicons_test_backup_20261023';
create temp table te on commit drop as select (x->>'id')::uuid id from app_config, jsonb_array_elements(value->'expenses') x where key='hicons_test_backup_20261023';
create temp table tc on commit drop as select (x->>'id')::uuid id from app_config, jsonb_array_elements(value->'contacts') x where key='hicons_test_backup_20261023';
delete from job_steps where job_id in (select id from tj);
delete from job_materials where job_id in (select id from tj);
delete from job_visits where job_id in (select id from tj);
delete from job_photos where job_id in (select id from tj);
delete from job_receipts where job_id in (select id from tj);
delete from contractor_expenses where id in (select id from te) and company='hicons';
update contractor_jobs set invoice_id = null where id in (select id from tj);
delete from contractor_invoices where id in (select id from ti) and company='hicons';
delete from contractor_jobs where id in (select id from tj) and company='hicons';
delete from contractor_contacts where id in (select id from tc) and company='hicons';
delete from contractor_projects where company='hicons' and name='test' and not exists (select 1 from contractor_jobs where project_id = contractor_projects.id);
update app_config set value = value || '{"invoice_next": 1001}'::jsonb where key='contractor_company_hicons';
commit;
