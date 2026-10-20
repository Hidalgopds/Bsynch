-- Removes the demo data created to try every contractor feature.
-- Everything it touches is marked: titles/vendors/visits start with "[TEST]",
-- invoice numbers start with "TEST-", contacts have source = 'test'.
delete from job_steps     where job_id in (select id from contractor_jobs where title like '[TEST]%');
delete from job_materials where job_id in (select id from contractor_jobs where title like '[TEST]%');
delete from job_visits    where job_id in (select id from contractor_jobs where title like '[TEST]%');
delete from job_photos    where job_id in (select id from contractor_jobs where title like '[TEST]%');
delete from contractor_expenses where vendor like '[TEST]%'
   or job_id in (select id from contractor_jobs where title like '[TEST]%');
update contractor_jobs set invoice_id = null where title like '[TEST]%';
delete from contractor_invoices where invoice_number like 'TEST-%';
delete from contractor_jobs     where title like '[TEST]%';
delete from contractor_contacts where source = 'test';
