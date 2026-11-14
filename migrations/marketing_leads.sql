-- Marketing: leads from the public sales page (/marketing).
-- Idempotent: safe to run more than once. Only in the main project (wanfpiogchwttsippekm):
-- the sales page lives on bsynch.com, never on a client company's database.

create table if not exists public.marketing_leads (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  name        text not null,
  company     text,
  email       text,
  phone       text,
  trade       text,
  crew_size   text,
  message     text,
  lang        text,
  source      text,
  status      text not null default 'new',   -- new, contacted, won, lost
  notes       text,
  updated_at  timestamptz,
  updated_by  text
);

create index if not exists marketing_leads_created_idx on public.marketing_leads (created_at desc);

-- Only the server (service key) reads and writes: RLS on, no policies.
alter table public.marketing_leads enable row level security;
