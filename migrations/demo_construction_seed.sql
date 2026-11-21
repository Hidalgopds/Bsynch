-- Sample data for the demo company "Demo Construction Co" (slug demo-construction, is_demo = true).
-- Everything here is invented: generic names, @example.com emails, 555 phones, sample addresses.
-- Runs once: does nothing if the demo company already has work orders. Main project only.
-- Allowed by CLAUDE.md: fake data only inside companies marked is_demo.

do $$
declare
  co text := 'demo-construction';
  p1 uuid; p2 uuid; p3 uuid;
  j1 uuid; j2 uuid; j3 uuid; j4 uuid; j5 uuid; j6 uuid; j7 uuid; j8 uuid;
  snap jsonb;
begin
  if not exists (select 1 from public.contractor_companies where slug = co and is_demo) then
    raise notice 'demo company missing or not marked demo: nothing done'; return;
  end if;
  if exists (select 1 from public.contractor_jobs where company = co) then
    raise notice 'demo already has data: nothing done'; return;
  end if;

  snap := jsonb_build_object('display_name', 'Demo Construction Co', 'subtitle', 'Remodeling · Roofing · Painting',
    'address', '100 Sample Ave, Houston, TX 77001', 'phone', '(555) 010-2000', 'emails', jsonb_build_array('office@example.com'),
    'contact_name', 'Office', 'invoice_prefix', 'D', 'invoice_pad', 6, 'payment_terms', 'Net 30',
    'payment_note', 'Pay by check or bank transfer.', 'footer_note', 'Thank you for your business!',
    'brand_primary', '#0d1b36', 'brand_accent', '#e8a317');

  -- Company profile (name, invoice numbering, contact) used by invoices and estimates
  insert into public.app_config (key, value, updated_at)
  values ('contractor_company_' || co, snap || jsonb_build_object('invoice_next', 105, 'reminder_days', 7), now())
  on conflict (key) do nothing;

  -- Clients
  insert into public.contractor_contacts (company, kind, name, org, emails, phones, channel, notes, source, created_by) values
    (co, 'client', 'Laura Martin', 'Oak Ridge Apartments', '["laura.martin@example.com"]', '["(555) 010-1001"]', 'email', 'Property manager, 3 buildings', 'demo', 'Demo'),
    (co, 'client', 'James Carter', null, '["james.carter@example.com"]', '["(555) 010-1002"]', 'phone', 'Homeowner, kitchen remodel', 'demo', 'Demo'),
    (co, 'client', 'Sofia Ramirez', 'Bayview Plaza', '["sofia.ramirez@example.com"]', '["(555) 010-1003"]', 'email', 'Retail center, roof and paint', 'demo', 'Demo'),
    (co, 'potential', 'Kevin Brooks', 'Brooks Dental', '["kevin.brooks@example.com"]', '["(555) 010-1004"]', 'phone', 'Asked for an office build-out quote', 'demo', 'Demo'),
    (co, 'worker', 'Miguel Torres', null, '["miguel.torres@example.com"]', '["(555) 010-1005"]', 'phone', 'Crew lead', 'demo', 'Demo');

  -- Projects
  insert into public.contractor_projects (name, description, client_name, status, created_by, company)
    values ('Oak Ridge Apartments', 'Unit turnovers and common areas', 'Laura Martin', 'active', 'Demo', co) returning id into p1;
  insert into public.contractor_projects (name, description, client_name, status, created_by, company)
    values ('Bayview Plaza', 'Roof repair and exterior paint', 'Sofia Ramirez', 'active', 'Demo', co) returning id into p2;
  insert into public.contractor_projects (name, description, client_name, status, created_by, company)
    values ('Carter Residence', 'Kitchen remodel', 'James Carter', 'active', 'Demo', co) returning id into p3;

  -- Work orders (dates relative to today so the demo always looks current)
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking,
      progress_pct, project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, created_by, assigned_to)
    values ('WO-001', 'Unit 204 turnover', 'Paint, patch walls, replace blinds', 'Laura Martin', 'laura.martin@example.com',
      '210 Oak Ridge Dr, Unit 204, Houston, TX', 'completed', 'normal', 'percent', 100, p1, co,
      current_date - 20, current_date - 15, current_date - 18, 'morning', 1850, 'Demo', 'Miguel Torres') returning id into j1;
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking,
      progress_pct, project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, created_by, assigned_to)
    values ('WO-002', 'Unit 112 turnover', 'Full paint and carpet clean', 'Laura Martin', 'laura.martin@example.com',
      '210 Oak Ridge Dr, Unit 112, Houston, TX', 'in_progress', 'normal', 'percent', 60, p1, co,
      current_date - 3, current_date + 2, current_date, 'morning', 1600, 'Demo', 'Miguel Torres') returning id into j2;
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking,
      progress_pct, project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, created_by)
    values ('WO-003', 'Lobby lighting upgrade', 'Replace 14 fixtures with LED', 'Laura Martin', 'laura.martin@example.com',
      '210 Oak Ridge Dr, Lobby, Houston, TX', 'open', 'normal', 'simple', 0, p1, co,
      current_date + 5, current_date + 7, current_date + 5, 'afternoon', 2400, 'Demo') returning id into j3;
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking,
      progress_pct, project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, created_by, assigned_to)
    values ('WO-004', 'Roof leak repair, section B', 'Replace damaged membrane and flashing', 'Sofia Ramirez', 'sofia.ramirez@example.com',
      '500 Bayview Blvd, Houston, TX', 'completed', 'high', 'percent', 100, p2, co,
      current_date - 30, current_date - 25, current_date - 28, 'morning', 6200, 'Demo', 'Miguel Torres') returning id into j4;
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking,
      progress_pct, project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, created_by, assigned_to)
    values ('WO-005', 'Exterior paint, front facade', 'Pressure wash, prime and paint', 'Sofia Ramirez', 'sofia.ramirez@example.com',
      '500 Bayview Blvd, Houston, TX', 'in_progress', 'normal', 'percent', 35, p2, co,
      current_date - 5, current_date + 10, current_date + 1, 'morning', 9800, 'Demo', 'Miguel Torres') returning id into j5;
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking,
      progress_pct, project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, created_by, needs_return, return_reason)
    values ('WO-006', 'Parking lot striping', 'Restripe 60 spaces and ADA signs', 'Sofia Ramirez', 'sofia.ramirez@example.com',
      '500 Bayview Blvd, Houston, TX', 'on_hold', 'normal', 'simple', 0, p2, co,
      current_date + 12, current_date + 14, null, '', 3100, 'Demo', true, 'Waiting for dry weather') returning id into j6;
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking,
      progress_pct, project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, created_by, assigned_to)
    values ('WO-007', 'Kitchen demolition', 'Remove cabinets, counters and tile', 'James Carter', 'james.carter@example.com',
      '45 Maple Ln, Katy, TX', 'completed', 'normal', 'percent', 100, p3, co,
      current_date - 12, current_date - 10, current_date - 12, 'morning', 2200, 'Demo', 'Miguel Torres') returning id into j7;
  insert into public.contractor_jobs (job_number, title, description, client_name, client_email, location, status, priority, tracking,
      progress_pct, project_id, company, start_date, due_date, scheduled_date, time_slot, service_price, created_by, assigned_to)
    values ('WO-008', 'Cabinets and countertops install', 'Install new cabinets, quartz tops and backsplash', 'James Carter', 'james.carter@example.com',
      '45 Maple Ln, Katy, TX', 'in_progress', 'high', 'percent', 45, p3, co,
      current_date - 4, current_date + 6, current_date + 2, 'afternoon', 14500, 'Demo', 'Miguel Torres') returning id into j8;

  -- Steps for the jobs tracked by percent
  insert into public.job_steps (job_id, step_name, order_num, progress_pct) values
    (j2, 'Patch and sand walls', 1, 100), (j2, 'Paint', 2, 60), (j2, 'Carpet clean', 3, 0),
    (j5, 'Pressure wash', 1, 100), (j5, 'Prime', 2, 40), (j5, 'Paint', 3, 0),
    (j8, 'Cabinets', 1, 90), (j8, 'Countertops', 2, 30), (j8, 'Backsplash', 3, 0);

  -- Site visits
  insert into public.job_visits (job_id, visit_date, description, hours, created_by) values
    (j2, current_date - 2, 'Walls patched, first coat in bedrooms', 6, 'Miguel Torres'),
    (j5, current_date - 3, 'Pressure wash done, scraping trim', 7.5, 'Miguel Torres'),
    (j8, current_date - 1, 'Upper cabinets hung and leveled', 8, 'Miguel Torres');

  -- Estimates
  insert into public.contractor_estimates (company, seq, estimate_number, title, client_name, client_email, location, items, subtotal, total,
      estimate_date, valid_until, status, public_token, company_snapshot, status_history, created_by, discount, tax_rate, tax) values
    (co, 1, 'EST-0001', 'Office build-out', 'Kevin Brooks', 'kevin.brooks@example.com', '900 Health Pkwy, Suite 3, Houston, TX',
      '[{"description":"Framing and drywall","qty":1,"amount":8400,"total":8400},{"description":"Electrical rough-in","qty":1,"amount":3900,"total":3900},{"description":"Paint and trim","qty":1,"amount":2700,"total":2700}]',
      15000, 15000, current_date - 2, current_date + 28, 'sent', replace(gen_random_uuid()::text, '-', ''), snap, '[]', 'Demo', 0, 0, 0),
    (co, 2, 'EST-0002', 'Lobby lighting upgrade', 'Laura Martin', 'laura.martin@example.com', '210 Oak Ridge Dr, Houston, TX',
      '[{"description":"LED fixtures","qty":14,"amount":120,"total":1680},{"description":"Labor","qty":1,"amount":720,"total":720}]',
      2400, 2400, current_date - 9, current_date + 21, 'accepted', replace(gen_random_uuid()::text, '-', ''), snap, '[]', 'Demo', 0, 0, 0),
    (co, 3, 'EST-0003', 'Bathroom refresh', 'James Carter', 'james.carter@example.com', '45 Maple Ln, Katy, TX',
      '[{"description":"Vanity and faucet","qty":1,"amount":1450,"total":1450},{"description":"Tile and labor","qty":1,"amount":2350,"total":2350}]',
      3800, 3800, current_date, current_date + 30, 'draft', replace(gen_random_uuid()::text, '-', ''), snap, '[]', 'Demo', 0, 0, 0);

  -- Invoices for the finished work
  insert into public.contractor_invoices (company, seq, invoice_number, job_id, bill_to, job_site, invoice_date, payment_terms, items,
      subtotal, total, company_snapshot, status, created_by, public_token, status_history, paid_at, discount, tax_rate, tax, due_date) values
    (co, 101, 'D000101', j4, 'Sofia Ramirez · Bayview Plaza', '500 Bayview Blvd, Houston, TX', current_date - 24, 'Net 30',
      '[{"description":"Roof leak repair, section B","qty":1,"amount":6200,"total":6200}]', 6200, 6200, snap, 'paid', 'Demo',
      replace(gen_random_uuid()::text, '-', ''), '[]', current_date - 6, 0, 0, 0, current_date + 6),
    (co, 102, 'D000102', j1, 'Laura Martin · Oak Ridge Apartments', '210 Oak Ridge Dr, Unit 204, Houston, TX', current_date - 14, 'Net 30',
      '[{"description":"Unit 204 turnover","qty":1,"amount":1850,"total":1850}]', 1850, 1850, snap, 'sent', 'Demo',
      replace(gen_random_uuid()::text, '-', ''), '[]', null, 0, 0, 0, current_date + 16),
    (co, 103, 'D000103', j7, 'James Carter', '45 Maple Ln, Katy, TX', current_date - 9, 'Due on receipt',
      '[{"description":"Kitchen demolition","qty":1,"amount":2200,"total":2200}]', 2200, 2200, snap, 'in_process', 'Demo',
      replace(gen_random_uuid()::text, '-', ''), '[]', null, 0, 0, 0, current_date - 9),
    (co, 104, 'D000104', null, 'Laura Martin · Oak Ridge Apartments', '210 Oak Ridge Dr, Houston, TX', current_date - 1, 'Net 30',
      '[{"description":"Emergency plumbing call","qty":1,"amount":450,"total":450}]', 450, 450, snap, 'issued', 'Demo',
      replace(gen_random_uuid()::text, '-', ''), '[]', null, 0, 0, 0, current_date + 29);

  -- Expenses (no receipt photos)
  insert into public.contractor_expenses (company, job_id, vendor, amount, tax, category, expense_date, description, payment_method, ai_read, added_by) values
    (co, j5, 'Sample Paint Supply', 642.18, 52.98, 'paint', current_date - 4, '15 gal exterior paint, primer', 'card', false, 'Miguel Torres'),
    (co, j8, 'Sample Home Center', 318.40, 26.27, 'materials', current_date - 3, 'Shims, screws, construction adhesive', 'card', false, 'Miguel Torres'),
    (co, j4, 'Sample Roofing Depot', 1490.00, 122.93, 'materials', current_date - 29, 'TPO membrane and flashing', 'card', false, 'Miguel Torres'),
    (co, null, 'Sample Fuel Stop', 86.50, 0, 'fuel', current_date - 2, 'Truck fuel', 'card', false, 'Miguel Torres'),
    (co, j5, 'Sample Equipment Rental', 275.00, 22.69, 'equipment_rental', current_date - 5, 'Pressure washer, 1 day', 'card', false, 'Miguel Torres');
end $$;
