-- Contractor module tables. Safe to re-run: only creates what is missing.
-- Each project / work order is tagged with its contractor company (hicons | bsynch).
-- RLS is on with no policies, like every other table: only the server key can read them.

create table if not exists contractor_projects (
  id          uuid primary key default gen_random_uuid(),
  name        text not null,
  description text default '',
  client_name text default '',
  status      text default 'active',
  created_by  text default '',
  company     text,
  created_at  timestamptz default now(),
  updated_at  timestamptz
);

create table if not exists contractor_jobs (
  id             uuid primary key default gen_random_uuid(),
  job_number     text,
  title          text not null,
  description    text default '',
  client_name    text default '',
  location       text default '',
  status         text default 'open',
  priority       text default 'normal',
  crew           jsonb default '[]'::jsonb,
  start_date     date,
  due_date       date,
  completed_date date,
  notes          text default '',
  created_by     text default '',
  progress_pct   numeric default 0,
  tracking       text default 'percent',
  project_id     uuid references contractor_projects(id) on delete set null,
  company        text,
  created_at     timestamptz default now(),
  updated_at     timestamptz
);

create table if not exists job_steps (
  id           uuid primary key default gen_random_uuid(),
  job_id       uuid not null references contractor_jobs(id) on delete cascade,
  step_name    text not null,
  order_num    int default 0,
  progress_pct numeric default 0,
  notes        text default '',
  created_at   timestamptz default now(),
  updated_at   timestamptz
);

create table if not exists job_materials (
  id            uuid primary key default gen_random_uuid(),
  job_id        uuid not null references contractor_jobs(id) on delete cascade,
  material_name text not null,
  qty           numeric default 0,
  unit          text default 'each',
  unit_cost     numeric default 0,
  notes         text default '',
  added_by      text default '',
  created_at    timestamptz default now()
);

create table if not exists job_photos (
  id          uuid primary key default gen_random_uuid(),
  job_id      uuid not null references contractor_jobs(id) on delete cascade,
  photo_data  text not null,
  caption     text default '',
  photo_type  text default 'progress',
  uploaded_by text default '',
  created_at  timestamptz default now()
);

-- Databases created before the company split
alter table contractor_projects add column if not exists company  text;
alter table contractor_jobs     add column if not exists company  text;
alter table contractor_jobs     add column if not exists tracking text default 'percent';
alter table app_users           add column if not exists contractor_company text;

create index if not exists contractor_projects_company_idx on contractor_projects (company);
create index if not exists contractor_jobs_company_idx     on contractor_jobs (company);
create index if not exists contractor_jobs_project_idx     on contractor_jobs (project_id);
create index if not exists job_steps_job_idx               on job_steps (job_id);
create index if not exists job_materials_job_idx           on job_materials (job_id);
create index if not exists job_photos_job_idx              on job_photos (job_id);

alter table contractor_projects enable row level security;
alter table contractor_jobs     enable row level security;
alter table job_steps           enable row level security;
alter table job_materials       enable row level security;
alter table job_photos          enable row level security;

-- Signed confidentiality + data-use agreements (one row per signature)
create table if not exists contractor_agreements (
  id             uuid primary key default gen_random_uuid(),
  user_name      text not null,
  company        text,
  version        text not null,
  agreement_text text not null,
  signer_name    text not null,
  signature_png  text not null,
  permissions    jsonb default '{}'::jsonb,
  ip             text,
  user_agent     text,
  signed_at      timestamptz default now()
);
create index if not exists contractor_agreements_user_idx    on contractor_agreements (user_name, version);
create index if not exists contractor_agreements_company_idx on contractor_agreements (company);
alter table contractor_agreements enable row level security;
