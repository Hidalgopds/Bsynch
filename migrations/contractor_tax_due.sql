-- Contractor: sales tax, discount and due date on invoices and estimates.
-- Safe to re-run: only adds what is missing. Nothing is deleted or rewritten.
-- Existing invoices/estimates keep their totals (discount, tax and rate start at 0).
-- Run it BEFORE publishing the code that uses these columns.

alter table contractor_invoices  add column if not exists discount numeric default 0;
alter table contractor_invoices  add column if not exists tax_rate numeric default 0;
alter table contractor_invoices  add column if not exists tax      numeric default 0;
alter table contractor_invoices  add column if not exists due_date date;

alter table contractor_estimates add column if not exists discount numeric default 0;
alter table contractor_estimates add column if not exists tax_rate numeric default 0;
alter table contractor_estimates add column if not exists tax      numeric default 0;

-- Old invoices: due on the invoice date ("Due on receipt"), so nothing changes for them.
update contractor_invoices set due_date = invoice_date where due_date is null and invoice_date is not null;

-- Both tables already have row level security on with no policies (only the server reads them).
alter table contractor_invoices  enable row level security;
alter table contractor_estimates enable row level security;
