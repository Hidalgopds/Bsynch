-- Contractor companies stop being fixed in the code. One shared database for every client:
-- each row of contractor data carries its company slug, and the server checks it on every call.
-- Idempotent. Only in the main project (wanfpiogchwttsippekm).

create table if not exists public.contractor_companies (
  slug        text primary key check (slug ~ '^[a-z][a-z0-9-]{1,29}$'),
  name        text not null,
  status      text not null default 'active' check (status in ('active', 'paused')),
  created_by  text default '',
  created_at  timestamptz not null default now()
);

-- Only the server (service key) reads or writes it.
alter table public.contractor_companies enable row level security;

insert into public.contractor_companies (slug, name, created_by)
values ('hicons', 'Hicons', 'migration'), ('bsynch', 'Bsynch', 'migration')
on conflict (slug) do nothing;
