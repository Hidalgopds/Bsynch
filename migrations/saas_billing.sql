-- SaaS: companies sign up on their own (wait for the owner's approval), free trial, Stripe billing.
-- Idempotent. Only in the main project (wanfpiogchwttsippekm). Nothing is deleted.

alter table public.contractor_companies add column if not exists contact_name text;
alter table public.contractor_companies add column if not exists contact_email text;
alter table public.contractor_companies add column if not exists contact_phone text;
alter table public.contractor_companies add column if not exists hubs jsonb not null default '["contractor"]'::jsonb;
alter table public.contractor_companies add column if not exists approved_by text;
alter table public.contractor_companies add column if not exists approved_at timestamptz;
alter table public.contractor_companies add column if not exists review_note text;
alter table public.contractor_companies add column if not exists trial_ends_at timestamptz;
-- none (signed up) | trial (our trial, no card) | Stripe: trialing, active, past_due, unpaid, canceled, incomplete...
alter table public.contractor_companies add column if not exists billing_status text not null default 'none';
alter table public.contractor_companies add column if not exists billing_exempt boolean not null default false;
alter table public.contractor_companies add column if not exists stripe_customer_id text;
alter table public.contractor_companies add column if not exists stripe_subscription_id text;

-- A sign-up waits as 'pending' until the owner approves or rejects it.
alter table public.contractor_companies drop constraint if exists contractor_companies_status_check;
alter table public.contractor_companies add constraint contractor_companies_status_check
  check (status in ('pending', 'active', 'paused', 'rejected'));

create index if not exists contractor_companies_status_idx on public.contractor_companies (status);
create index if not exists contractor_companies_sub_idx on public.contractor_companies (stripe_subscription_id);

-- The original companies never get a bill.
update public.contractor_companies set billing_exempt = true where slug in ('hicons', 'bsynch') and billing_exempt = false;
