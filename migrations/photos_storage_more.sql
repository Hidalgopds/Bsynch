-- More images move out of the database into private Storage (Settings, 2026-11-21).
-- The app moves them on its own, a few every 10 minutes (_storage_autopilot); the database copy is
-- cleared only after Storage confirms it holds the file. Idempotent. Main project only.

-- Where each image lives once moved (path inside its bucket)
alter table public.homelab_kid_photos add column if not exists photo_path text;
alter table public.homelab_kid_photos alter column photo_data drop not null;
alter table public.homelab_tasks add column if not exists task_image_path text;
alter table public.contractor_expenses add column if not exists photo_path text;

-- Kids' photos and task pictures: their own private bucket, apart from company files.
-- No policies on it: only the server (service key) reads or writes; the app serves each image
-- after its own checks.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('family-photos', 'family-photos', false, 6000000, array['image/jpeg', 'image/png', 'image/webp'])
on conflict (id) do update
  set public = false,
      file_size_limit = excluded.file_size_limit,
      allowed_mime_types = excluded.allowed_mime_types;
