-- One-time links to set (new account) or reset (forgot) a password. Replaces the old
-- "temporary password" reset, which let anyone change someone else's password.
-- Only a SHA-256 hash of each link is stored. Idempotent. Main project (wanfpiogchwttsippekm).

create table if not exists public.password_links (
  id          uuid primary key default gen_random_uuid(),
  token_hash  text not null unique,
  user_name   text not null,
  purpose     text not null check (purpose in ('setup', 'reset')),
  expires_at  timestamptz not null,
  used_at     timestamptz,
  used_note   text,
  created_by  text default '',
  created_at  timestamptz not null default now()
);

create index if not exists password_links_user_idx on public.password_links (user_name) where used_at is null;

-- Only the server (service key) reads or writes it.
alter table public.password_links enable row level security;
