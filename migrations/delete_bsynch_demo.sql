-- Removes the Bsynch demo data shown to prospective clients.
-- Every id is listed in app_config 'bsynch_demo_ids' (jobs B-101..B-118, invoices BS-*, estimates EST-1001..1006,
-- demo expenses, contacts with source = 'demo'). The company profile and alert settings stay.
with ids as (select value v from app_config where key = 'bsynch_demo_ids')
delete from job_steps     where job_id in (select jsonb_array_elements_text(v->'jobs')::uuid from ids);
with ids as (select value v from app_config where key = 'bsynch_demo_ids')
delete from job_materials where job_id in (select jsonb_array_elements_text(v->'jobs')::uuid from ids);
with ids as (select value v from app_config where key = 'bsynch_demo_ids')
delete from job_visits    where job_id in (select jsonb_array_elements_text(v->'jobs')::uuid from ids);
with ids as (select value v from app_config where key = 'bsynch_demo_ids')
delete from job_photos    where job_id in (select jsonb_array_elements_text(v->'jobs')::uuid from ids);
with ids as (select value v from app_config where key = 'bsynch_demo_ids')
delete from contractor_estimates where id in (select jsonb_array_elements_text(coalesce(v->'estimates', '[]'::jsonb))::uuid from ids);
with ids as (select value v from app_config where key = 'bsynch_demo_ids')
delete from contractor_expenses where id in (select jsonb_array_elements_text(v->'expenses')::uuid from ids);
with ids as (select value v from app_config where key = 'bsynch_demo_ids')
update contractor_jobs set invoice_id = null where id in (select jsonb_array_elements_text(v->'jobs')::uuid from ids);
with ids as (select value v from app_config where key = 'bsynch_demo_ids')
delete from contractor_invoices where id in (select jsonb_array_elements_text(v->'invoices')::uuid from ids);
with ids as (select value v from app_config where key = 'bsynch_demo_ids')
delete from contractor_jobs     where id in (select jsonb_array_elements_text(v->'jobs')::uuid from ids);
with ids as (select value v from app_config where key = 'bsynch_demo_ids')
delete from contractor_contacts where id in (select jsonb_array_elements_text(v->'contacts')::uuid from ids);
delete from app_config where key in ('bsynch_demo_ids', 'demo_write_probe');
