-- Contractor hub: tag projects and work orders with the contractor company
-- (hicons | bsynch) so each company only sees its own data.
-- Run once in the Supabase SQL editor of every database that holds contractor_projects.

alter table contractor_projects add column if not exists company text;
alter table contractor_jobs     add column if not exists company text;

create index if not exists contractor_projects_company_idx on contractor_projects (company);
create index if not exists contractor_jobs_company_idx     on contractor_jobs (company);

-- Users are assigned to a company through app_users.contractor_company.
alter table app_users add column if not exists contractor_company text;
