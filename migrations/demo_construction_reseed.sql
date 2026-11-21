-- Rebuilds the sample data of "Demo Construction Co" (slug demo-construction, is_demo = true). Owner's request, 2026-11-21:
-- invented data (nothing real) that shows every Contractor function: contacts of every kind and channel with folders,
-- projects, work orders in every status and priority (calendar this week and next), steps, visits, materials,
-- receipts, estimates in every status, invoices in every status (one overdue), expenses in every category, mail room.
-- Invented town "Sampleton, TX", streets "Example/Sample", @example.com emails, (555) phones.
-- Only touches rows of the demo company, and only if it is marked is_demo (CLAUDE.md: fake data only in is_demo companies).
-- Safe to run again: it clears the demo company's rows and loads them fresh. Main project only.

do $$
declare
  co text := 'demo-construction';
  f1 uuid; f2 uuid;
  p1 uuid; p2 uuid; p3 uuid; p4 uuid;
  j uuid[] := array[]::uuid[];
  jid uuid;
  i1 uuid; i2 uuid; i3 uuid; i4 uuid; i5 uuid; i6 uuid;
  snap jsonb;
begin
  if not exists (select 1 from public.contractor_companies where slug = co and is_demo) then
    raise notice 'demo company missing or not marked demo: nothing done'; return;
  end if;

  -- 1) Clear the demo company's rows (demo only; real companies are never touched)
  update public.contractor_jobs set invoice_id = null where company = co;
  delete from public.job_photos    where job_id in (select id from public.contractor_jobs where company = co);
  delete from public.job_steps     where job_id in (select id from public.contractor_jobs where company = co);
  delete from public.job_visits    where job_id in (select id from public.contractor_jobs where company = co);
  delete from public.job_materials where job_id in (select id from public.contractor_jobs where company = co);
  delete from public.job_receipts  where job_id in (select id from public.contractor_jobs where company = co);
  delete from public.contractor_expenses  where company = co;
  delete from public.contractor_invoices  where company = co;
  delete from public.contractor_estimates where company = co;
  delete from public.contractor_jobs      where company = co;
  delete from public.contractor_projects  where company = co;
  delete from public.contractor_contacts  where company = co;
  delete from public.contractor_client_folders where company = co;
  delete from public.contractor_mail_log  where company = co;

  -- 2) Company profile used by invoices and estimates
  snap := jsonb_build_object('display_name', 'Demo Construction Co', 'subtitle', 'Remodeling · Roofing · Painting · Make-ready',
    'address', '100 Example Ave, Sampleton, TX 77000', 'phone', '(555) 010-2000', 'emails', jsonb_build_array('office@example.com'),
    'contact_name', 'Front Office', 'invoice_prefix', 'D', 'invoice_pad', 6, 'payment_terms', 'Net 30',
    'payment_note', 'Pay by check or bank transfer. This is sample data.', 'footer_note', 'Thank you for your business! (Demo company)',
    'brand_primary', '#0d1b36', 'brand_accent', '#e8a317');
  insert into public.app_config (key, value, updated_at)
  values ('contractor_company_' || co, snap || jsonb_build_object('invoice_next', 107, 'reminder_days', 7), now())
  on conflict (key) do update set value = excluded.value, updated_at = now();

  -- 3) Contact folders and contacts (every kind, every channel)
  insert into public.contractor_client_folders (company, name, color, sort, created_by) values (co, 'Property managers', '#0f766e', 1, 'Demo') returning id into f1;
  insert into public.contractor_client_folders (company, name, color, sort, created_by) values (co, 'Homeowners', '#e8a317', 2, 'Demo') returning id into f2;
  insert into public.contractor_contacts (company, kind, name, org, role_desc, emails, phones, channel, notes, source, created_by, folder_id) values
    (co, 'client', 'Laura Bennett', 'Pinecrest Apartments', 'Property manager', '["laura.bennett@example.com"]', '["(555) 010-1001"]', 'email', '3 buildings, 120 units. Prefers email with photos.', 'demo', 'Demo', f1),
    (co, 'client', 'Victor Hale', 'Harbor Point Plaza', 'Project manager', '["victor.hale@example.com"]', '["(555) 010-1002"]', 'call', 'Retail center. Roof and exterior.', 'demo', 'Demo', f1),
    (co, 'client', 'Nora Castillo', 'Willow Creek Lofts', 'Superintendent', '["nora.castillo@example.com"]', '["(555) 010-1003"]', 'whatsapp', 'Make-ready turns every month.', 'demo', 'Demo', f1),
    (co, 'client', 'James Whitfield', null, 'End client', '["james.whitfield@example.com"]', '["(555) 010-1004"]', 'text', 'Kitchen remodel. Works from home, call after 10 am.', 'demo', 'Demo', f2),
    (co, 'client', 'Priya Raman', null, 'End client', '["priya.raman@example.com"]', '["(555) 010-1005"]', 'email', 'Bathroom and fence.', 'demo', 'Demo', f2),
    (co, 'potential', 'Kevin Brooks', 'Brooks Family Dental', 'End client', '["kevin.brooks@example.com"]', '["(555) 010-1006"]', 'call', 'Asked for an office build-out quote.', 'demo', 'Demo', null),
    (co, 'potential', 'Megan Doyle', 'Sunrise Builders', 'Builder', '["megan.doyle@example.com"]', '["(555) 010-1007"]', 'email', 'Possible subcontract work on new homes.', 'demo', 'Demo', null),
    (co, 'worker', 'Miguel Torres', null, 'Painter', '["miguel.torres@example.com"]', '["(555) 010-1101"]', 'whatsapp', 'Crew lead. Paint and drywall.', 'demo', 'Demo', null),
    (co, 'worker', 'Andre Wallace', null, 'Electrician', '["andre.wallace@example.com"]', '["(555) 010-1102"]', 'text', 'Licensed electrician (sample).', 'demo', 'Demo', null),
    (co, 'worker', 'Rosa Medina', null, 'Sheetrock', '["rosa.medina@example.com"]', '["(555) 010-1103"]', 'call', 'Drywall and texture.', 'demo', 'Demo', null),
    (co, 'other', 'Sample Supply Co', 'Sample Supply Co', 'Supplier', '["orders@example.com"]', '["(555) 010-1201"]', 'email', 'Paint and materials account #DEMO-001.', 'demo', 'Demo', null);

  -- 4) Projects
  insert into public.contractor_projects (name, description, client_name, status, created_by, company)
    values ('Pinecrest Apartments', 'Unit turnovers and common areas', 'Laura Bennett', 'active', 'Demo', co) returning id into p1;
  insert into public.contractor_projects (name, description, client_name, status, created_by, company)
    values ('Harbor Point Plaza', 'Roof repair, exterior paint, parking lot', 'Victor Hale', 'active', 'Demo', co) returning id into p2;
  insert into public.contractor_projects (name, description, client_name, status, created_by, company)
    values ('Whitfield Residence', 'Kitchen remodel', 'James Whitfield', 'active', 'Demo', co) returning id into p3;
  insert into public.contractor_projects (name, description, client_name, status, created_by, company)
    values ('Willow Creek Lofts', 'Monthly make-ready turns', 'Nora Castillo', 'active', 'Demo', co) returning id into p4;

  -- 5) Work orders: every status (open, in_progress, on_hold, completed, cancelled), every priority,
  --    simple and percent tracking, morning/afternoon, spread over last month, this week and next week.
  -- j[1] completed + paid
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking, progress_pct,
      project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, est_hours, created_by, assigned_to, completed_date, zone, zipcode)
    values ('WO-001', 'Roof leak repair, section B', 'Replace damaged membrane and flashing', 'Victor Hale', 'victor.hale@example.com',
      '500 Sample Blvd, Sampleton, TX', 'completed', 'urgent', 'percent', 100, p2, co, current_date - 34, current_date - 30, current_date - 33,
      'morning', 6200, 16, 'Demo', 'Miguel Torres', current_date - 30, 'North', '77000') returning id into jid; j := j || jid;
  -- j[2] completed + sent invoice
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking, progress_pct,
      project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, est_hours, created_by, assigned_to, completed_date, apt, zone, zipcode)
    values ('WO-002', 'Unit 204 turnover', 'Paint, patch walls, replace blinds', 'Laura Bennett', 'laura.bennett@example.com',
      '210 Example Dr, Sampleton, TX', 'completed', 'normal', 'percent', 100, p1, co, current_date - 20, current_date - 15, current_date - 18,
      'morning', 1850, 10, 'Demo', 'Miguel Torres', current_date - 16, '204', 'North', '77000') returning id into jid; j := j || jid;
  -- j[3] completed + in-process invoice
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking, progress_pct,
      project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, est_hours, created_by, assigned_to, completed_date, zone, zipcode)
    values ('WO-003', 'Kitchen demolition', 'Remove cabinets, counters and tile', 'James Whitfield', 'james.whitfield@example.com',
      '45 Sample Ln, Sampleton, TX', 'completed', 'normal', 'simple', 100, p3, co, current_date - 12, current_date - 10, current_date - 12,
      'morning', 2200, 8, 'Demo', 'Rosa Medina', current_date - 11, 'West', '77001') returning id into jid; j := j || jid;
  -- j[4] completed, NOT invoiced yet (shows "ready to invoice")
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking, progress_pct,
      project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, est_hours, created_by, assigned_to, completed_date, apt, zone, zipcode)
    values ('WO-004', 'Unit 3C make-ready', 'Paint, clean, change locks, replace 2 outlets', 'Nora Castillo', 'nora.castillo@example.com',
      '88 Example Way, Sampleton, TX', 'completed', 'high', 'percent', 100, p4, co, current_date - 4, current_date - 2, current_date - 3,
      'afternoon', 1450, 9, 'Demo', 'Miguel Torres', current_date - 2, '3C', 'East', '77002') returning id into jid; j := j || jid;
  -- j[5] in progress, today
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking, progress_pct,
      project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, est_hours, created_by, assigned_to, apt, zone, zipcode)
    values ('WO-005', 'Unit 112 turnover', 'Full paint and carpet clean', 'Laura Bennett', 'laura.bennett@example.com',
      '210 Example Dr, Sampleton, TX', 'in_progress', 'normal', 'percent', 60, p1, co, current_date - 3, current_date + 2, current_date,
      'morning', 1600, 12, 'Demo', 'Miguel Torres', '112', 'North', '77000') returning id into jid; j := j || jid;
  -- j[6] in progress, tomorrow
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking, progress_pct,
      project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, est_hours, created_by, assigned_to, zone, zipcode)
    values ('WO-006', 'Exterior paint, front facade', 'Pressure wash, prime and paint', 'Victor Hale', 'victor.hale@example.com',
      '500 Sample Blvd, Sampleton, TX', 'in_progress', 'normal', 'percent', 35, p2, co, current_date - 5, current_date + 10, current_date + 1,
      'morning', 9800, 40, 'Demo', 'Miguel Torres', 'North', '77000') returning id into jid; j := j || jid;
  -- j[7] in progress, high priority, in 2 days
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking, progress_pct,
      project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, est_hours, created_by, assigned_to, zone, zipcode)
    values ('WO-007', 'Cabinets and countertops install', 'Install new cabinets, quartz tops and backsplash', 'James Whitfield', 'james.whitfield@example.com',
      '45 Sample Ln, Sampleton, TX', 'in_progress', 'high', 'percent', 45, p3, co, current_date - 4, current_date + 6, current_date + 2,
      'afternoon', 14500, 32, 'Demo', 'Rosa Medina', 'West', '77001') returning id into jid; j := j || jid;
  -- j[8] open, this week
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking, progress_pct,
      project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, est_hours, created_by, assigned_to, zone, zipcode)
    values ('WO-008', 'Lobby lighting upgrade', 'Replace 14 fixtures with LED', 'Laura Bennett', 'laura.bennett@example.com',
      '210 Example Dr, Lobby, Sampleton, TX', 'open', 'normal', 'simple', 0, p1, co, current_date + 3, current_date + 4, current_date + 3,
      'afternoon', 2400, 8, 'Demo', 'Andre Wallace', 'North', '77000') returning id into jid; j := j || jid;
  -- j[9] open, next week, low priority, nobody assigned yet
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking, progress_pct,
      project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, est_hours, created_by, zone, zipcode)
    values ('WO-009', 'Backyard fence repair', 'Replace 6 pickets and one post', 'Priya Raman', 'priya.raman@example.com',
      '12 Example Ct, Sampleton, TX', 'open', 'low', 'simple', 0, null, co, current_date + 8, current_date + 9, current_date + 8,
      'morning', 650, 4, 'Demo', 'South', '77003') returning id into jid; j := j || jid;
  -- j[10] open, not scheduled yet
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking, progress_pct,
      project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, est_hours, created_by, apt, zone, zipcode)
    values ('WO-010', 'Unit 5A make-ready', 'Paint and deep clean after move-out', 'Nora Castillo', 'nora.castillo@example.com',
      '88 Example Way, Sampleton, TX', 'open', 'normal', 'simple', 0, p4, co, null, current_date + 12, null,
      '', 1300, 8, 'Demo', '5A', 'East', '77002') returning id into jid; j := j || jid;
  -- j[11] on hold, needs a return visit
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking, progress_pct,
      project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, est_hours, created_by, needs_return, return_reason, return_requested_at, zone, zipcode)
    values ('WO-011', 'Parking lot striping', 'Restripe 60 spaces and ADA signs', 'Victor Hale', 'victor.hale@example.com',
      '500 Sample Blvd, Sampleton, TX', 'on_hold', 'normal', 'simple', 0, p2, co, current_date + 12, current_date + 14, null,
      '', 3100, 12, 'Demo', true, 'Waiting for dry weather', now() - interval '1 day', 'North', '77000') returning id into jid; j := j || jid;
  -- j[12] cancelled
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking, progress_pct,
      project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, est_hours, created_by, notes, zone, zipcode)
    values ('WO-012', 'Gutter cleaning', 'Clean and flush gutters, 2 buildings', 'Laura Bennett', 'laura.bennett@example.com',
      '210 Example Dr, Sampleton, TX', 'cancelled', 'low', 'simple', 0, p1, co, current_date - 6, current_date - 5, null,
      '', 480, 4, 'Demo', 'Client will do it with their own staff.', 'North', '77000') returning id into jid; j := j || jid;
  -- j[13] completed earlier, paid (gives the dashboard last month's revenue)
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking, progress_pct,
      project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, est_hours, created_by, assigned_to, completed_date, zone, zipcode)
    values ('WO-013', 'Bathroom refresh', 'New vanity, faucet and tile', 'Priya Raman', 'priya.raman@example.com',
      '12 Example Ct, Sampleton, TX', 'completed', 'normal', 'percent', 100, null, co, current_date - 45, current_date - 40, current_date - 44,
      'morning', 3800, 18, 'Demo', 'Rosa Medina', current_date - 41, 'South', '77003') returning id into jid; j := j || jid;

  -- 6) Steps, visits, materials and receipts (no photos)
  insert into public.job_steps (job_id, step_name, order_num, progress_pct) values
    (j[5], 'Patch and sand walls', 1, 100), (j[5], 'Paint', 2, 60), (j[5], 'Carpet clean', 3, 0),
    (j[6], 'Pressure wash', 1, 100), (j[6], 'Prime', 2, 40), (j[6], 'Paint', 3, 0),
    (j[7], 'Cabinets', 1, 90), (j[7], 'Countertops', 2, 30), (j[7], 'Backsplash', 3, 0),
    (j[1], 'Tear off', 1, 100), (j[1], 'Membrane', 2, 100), (j[1], 'Flashing', 3, 100),
    (j[4], 'Paint', 1, 100), (j[4], 'Clean', 2, 100), (j[4], 'Locks and outlets', 3, 100);
  insert into public.job_visits (job_id, visit_date, description, hours, created_by) values
    (j[1], current_date - 33, 'Tear off and dry-in', 8, 'Miguel Torres'),
    (j[1], current_date - 31, 'New membrane and flashing, water test OK', 8, 'Miguel Torres'),
    (j[4], current_date - 3, 'Paint and clean done', 6, 'Miguel Torres'),
    (j[4], current_date - 2, 'Locks changed, outlets replaced', 3, 'Andre Wallace'),
    (j[5], current_date - 2, 'Walls patched, first coat in bedrooms', 6, 'Miguel Torres'),
    (j[6], current_date - 3, 'Pressure wash done, scraping trim', 7.5, 'Miguel Torres'),
    (j[7], current_date - 1, 'Upper cabinets hung and leveled', 8, 'Rosa Medina');
  insert into public.job_materials (job_id, material_name, qty, unit, unit_cost, notes, added_by) values
    (j[5], 'Interior paint, eggshell', 5, 'gal', 38.50, 'Color: Sample White', 'Miguel Torres'),
    (j[5], 'Joint compound', 1, 'bucket', 18.00, null, 'Miguel Torres'),
    (j[6], 'Exterior paint', 15, 'gal', 42.00, null, 'Miguel Torres'),
    (j[6], 'Primer', 5, 'gal', 29.00, null, 'Miguel Torres'),
    (j[7], 'Cabinet screws', 2, 'box', 12.50, null, 'Rosa Medina'),
    (j[1], 'TPO membrane', 4, 'roll', 310.00, null, 'Miguel Torres'),
    (j[4], 'Door lock set', 2, 'each', 34.00, null, 'Andre Wallace');
  insert into public.job_receipts (job_id, vendor, amount, receipt_date, notes, added_by) values
    (j[5], 'Sample Paint Supply', 210.50, current_date - 3, 'Paint and compound (sample)', 'Miguel Torres'),
    (j[1], 'Sample Roofing Depot', 1490.00, current_date - 34, 'Membrane and flashing (sample)', 'Miguel Torres');

  -- 7) Estimates: draft, sent, accepted, declined, converted (one with discount and tax)
  insert into public.contractor_estimates (company, seq, estimate_number, title, client_name, client_email, location, items, subtotal, total,
      estimate_date, valid_until, status, public_token, company_snapshot, status_history, created_by, discount, tax_rate, tax) values
    (co, 1, 'EST-0001', 'Office build-out', 'Kevin Brooks', 'kevin.brooks@example.com', '900 Sample Pkwy, Suite 3, Sampleton, TX',
      '[{"description":"Framing and drywall","qty":1,"amount":8400,"total":8400},{"description":"Electrical rough-in","qty":1,"amount":3900,"total":3900},{"description":"Paint and trim","qty":1,"amount":2700,"total":2700}]',
      15000, 14250, current_date - 2, current_date + 28, 'sent', replace(gen_random_uuid()::text, '-', ''), snap, '[]', 'Demo', 750, 0, 0),
    (co, 2, 'EST-0002', 'Lobby lighting upgrade', 'Laura Bennett', 'laura.bennett@example.com', '210 Example Dr, Sampleton, TX',
      '[{"description":"LED fixtures","qty":14,"amount":120,"total":1680},{"description":"Labor","qty":1,"amount":720,"total":720}]',
      2400, 2400, current_date - 9, current_date + 21, 'accepted', replace(gen_random_uuid()::text, '-', ''), snap, '[]', 'Demo', 0, 0, 0),
    (co, 3, 'EST-0003', 'Deck staining', 'Priya Raman', 'priya.raman@example.com', '12 Example Ct, Sampleton, TX',
      '[{"description":"Clean and stain deck, 300 sq ft","qty":300,"amount":3.5,"total":1050}]',
      1050, 1050, current_date, current_date + 30, 'draft', replace(gen_random_uuid()::text, '-', ''), snap, '[]', 'Demo', 0, 0, 0),
    (co, 4, 'EST-0004', 'New homes, interior paint (per house)', 'Megan Doyle', 'megan.doyle@example.com', 'Sample Meadows subdivision, Sampleton, TX',
      '[{"description":"Interior paint, 2,000 sq ft house","qty":1,"amount":5600,"total":5600}]',
      5600, 6062, current_date - 20, current_date + 10, 'declined', replace(gen_random_uuid()::text, '-', ''), snap, '[]', 'Demo', 0, 8.25, 462),
    (co, 5, 'EST-0005', 'Cabinets and countertops', 'James Whitfield', 'james.whitfield@example.com', '45 Sample Ln, Sampleton, TX',
      '[{"description":"Cabinets","qty":1,"amount":8200,"total":8200},{"description":"Quartz countertops","qty":1,"amount":4800,"total":4800},{"description":"Backsplash","qty":1,"amount":1500,"total":1500}]',
      14500, 14500, current_date - 15, current_date + 15, 'converted', replace(gen_random_uuid()::text, '-', ''), snap, '[]', 'Demo', 0, 0, 0);

  -- 8) Invoices: paid, sent, in process, not sent, overdue, and one with tax
  insert into public.contractor_invoices (company, seq, invoice_number, job_id, bill_to, job_site, invoice_date, payment_terms, items,
      subtotal, total, company_snapshot, status, created_by, public_token, status_history, paid_at, discount, tax_rate, tax, due_date) values
    (co, 101, 'D000101', j[1], 'Victor Hale · Harbor Point Plaza', '500 Sample Blvd, Sampleton, TX', current_date - 29, 'Net 30',
      '[{"description":"Roof leak repair, section B","qty":1,"amount":6200,"total":6200}]', 6200, 6200, snap, 'paid', 'Demo',
      replace(gen_random_uuid()::text, '-', ''), '[]', current_date - 8, 0, 0, 0, current_date + 1)
    returning id into i1;
  insert into public.contractor_invoices (company, seq, invoice_number, job_id, bill_to, job_site, invoice_date, payment_terms, items,
      subtotal, total, company_snapshot, status, created_by, public_token, status_history, paid_at, discount, tax_rate, tax, due_date) values
    (co, 102, 'D000102', j[2], 'Laura Bennett · Pinecrest Apartments', '210 Example Dr, Unit 204, Sampleton, TX', current_date - 15, 'Net 30',
      '[{"description":"Unit 204 turnover","qty":1,"amount":1850,"total":1850}]', 1850, 1850, snap, 'sent', 'Demo',
      replace(gen_random_uuid()::text, '-', ''), '[]', null, 0, 0, 0, current_date + 15)
    returning id into i2;
  insert into public.contractor_invoices (company, seq, invoice_number, job_id, bill_to, job_site, invoice_date, payment_terms, items,
      subtotal, total, company_snapshot, status, created_by, public_token, status_history, paid_at, discount, tax_rate, tax, due_date) values
    (co, 103, 'D000103', j[3], 'James Whitfield', '45 Sample Ln, Sampleton, TX', current_date - 10, 'Due on receipt',
      '[{"description":"Kitchen demolition","qty":1,"amount":2200,"total":2200}]', 2200, 2200, snap, 'in_process', 'Demo',
      replace(gen_random_uuid()::text, '-', ''), '[]', null, 0, 0, 0, current_date - 10)
    returning id into i3;
  insert into public.contractor_invoices (company, seq, invoice_number, job_id, bill_to, job_site, invoice_date, payment_terms, items,
      subtotal, total, company_snapshot, status, created_by, public_token, status_history, paid_at, discount, tax_rate, tax, due_date) values
    (co, 104, 'D000104', null, 'Laura Bennett · Pinecrest Apartments', '210 Example Dr, Sampleton, TX', current_date - 1, 'Net 30',
      '[{"description":"Emergency plumbing call (sample)","qty":1,"amount":450,"total":450}]', 450, 450, snap, 'issued', 'Demo',
      replace(gen_random_uuid()::text, '-', ''), '[]', null, 0, 0, 0, current_date + 29)
    returning id into i4;
  insert into public.contractor_invoices (company, seq, invoice_number, job_id, bill_to, job_site, invoice_date, payment_terms, items,
      subtotal, total, company_snapshot, status, created_by, public_token, status_history, paid_at, discount, tax_rate, tax, due_date) values
    (co, 105, 'D000105', null, 'Nora Castillo · Willow Creek Lofts', '88 Example Way, Sampleton, TX', current_date - 40, 'Net 30',
      '[{"description":"Unit 2B make-ready","qty":1,"amount":1380,"total":1380}]', 1380, 1380, snap, 'sent', 'Demo',
      replace(gen_random_uuid()::text, '-', ''), '[]', null, 0, 0, 0, current_date - 10)
    returning id into i5;
  insert into public.contractor_invoices (company, seq, invoice_number, job_id, bill_to, job_site, invoice_date, payment_terms, items,
      subtotal, total, company_snapshot, status, created_by, public_token, status_history, paid_at, discount, tax_rate, tax, due_date) values
    (co, 106, 'D000106', j[13], 'Priya Raman', '12 Example Ct, Sampleton, TX', current_date - 40, 'Net 15',
      '[{"description":"Vanity and faucet","qty":1,"amount":1450,"total":1450},{"description":"Tile and labor","qty":1,"amount":2350,"total":2350}]',
      3800, 4113.50, snap, 'paid', 'Demo', replace(gen_random_uuid()::text, '-', ''), '[]', current_date - 30, 0, 8.25, 313.50, current_date - 25)
    returning id into i6;
  update public.contractor_jobs set invoice_id = i1 where id = j[1];
  update public.contractor_jobs set invoice_id = i2 where id = j[2];
  update public.contractor_jobs set invoice_id = i3 where id = j[3];
  update public.contractor_jobs set invoice_id = i6 where id = j[13];

  -- 9) Expenses: every category, several payment methods, this month and last month (no receipt photos)
  insert into public.contractor_expenses (company, job_id, vendor, amount, tax, category, expense_date, description, payment_method, ai_read, added_by) values
    (co, j[6], 'Sample Paint Supply', 642.18, 52.98, 'paint', current_date - 4, '15 gal exterior paint, primer', 'Company card', false, 'Miguel Torres'),
    (co, j[7], 'Sample Home Center', 318.40, 26.27, 'materials', current_date - 3, 'Shims, screws, construction adhesive', 'Company card', false, 'Rosa Medina'),
    (co, j[1], 'Sample Roofing Depot', 1490.00, 122.93, 'materials', current_date - 34, 'TPO membrane and flashing', 'Company card', false, 'Miguel Torres'),
    (co, null, 'Sample Fuel Stop', 86.50, 0, 'fuel', current_date - 2, 'Truck fuel', 'Company card', false, 'Miguel Torres'),
    (co, null, 'Sample Fuel Stop', 74.20, 0, 'fuel', current_date - 33, 'Truck fuel', 'Cash', false, 'Miguel Torres'),
    (co, j[6], 'Sample Equipment Rental', 275.00, 22.69, 'equipment_rental', current_date - 5, 'Pressure washer, 1 day', 'Company card', false, 'Miguel Torres'),
    (co, null, 'Sample Tool Store', 189.99, 15.67, 'tools', current_date - 9, 'Cordless drill kit', 'Company card', false, 'Andre Wallace'),
    (co, j[4], 'Sample Truck Service', 120.00, 9.90, 'repairs', current_date - 6, 'Van tire repair', 'Check #1001', false, 'Front Office'),
    (co, j[1], 'Sample Diner', 48.60, 4.01, 'meals', current_date - 31, 'Crew lunch, long roof day', 'Company card', false, 'Miguel Torres'),
    (co, j[5], 'Sample Supply Co', 64.35, 5.31, 'supplies', current_date - 2, 'Drop cloths, tape, rollers', 'Company card', false, 'Miguel Torres'),
    (co, null, 'Sample Print Shop', 35.00, 2.89, 'other', current_date - 12, 'Door hangers (sample)', 'Cash', false, 'Front Office'),
    (co, j[13], 'Sample Tile Outlet', 610.00, 50.33, 'materials', current_date - 44, 'Porcelain tile and grout', 'Company card', false, 'Rosa Medina');

  -- 10) Mail room: what the app "sent" (sample log only; no email goes out)
  insert into public.contractor_mail_log (company, kind, ref, to_addrs, subject, status, via, sent_by, created_at) values
    (co, 'invoice', 'D000102', 'laura.bennett@example.com', 'Invoice D000102 from Demo Construction Co', 'sent', 'demo', 'Front Office', now() - interval '15 days'),
    (co, 'invoice', 'D000105', 'nora.castillo@example.com', 'Invoice D000105 from Demo Construction Co', 'sent', 'demo', 'Front Office', now() - interval '40 days'),
    (co, 'alert:invoice_overdue', 'D000105', 'office@example.com', 'Overdue: invoice D000105', 'sent', 'demo', 'BSynch', now() - interval '9 days'),
    (co, 'alert:wo_created', 'WO-009', 'office@example.com', 'New work order WO-009', 'sent', 'demo', 'BSynch', now() - interval '1 day'),
    (co, 'alert:job_finished', 'WO-004', 'office@example.com', 'Finished: WO-004 Unit 3C make-ready', 'sent', 'demo', 'BSynch', now() - interval '2 days'),
    (co, 'alert:tomorrow_jobs', '', 'office@example.com', 'Tomorrow: 1 work order', 'sent', 'demo', 'BSynch', now() - interval '12 hours');
end $$;
