-- Work-order photos move from the database to Supabase Storage.
-- Idempotent: safe to run more than once. Run it in every Supabase project that has job_photos
-- (principal wanfpiogchwttsippekm and client companies such as NNC).

-- 1) Where the photo now lives (path inside the bucket). Old photos keep photo_data until moved.
alter table public.job_photos add column if not exists storage_path text;
alter table public.job_photos alter column photo_data drop not null;

-- 2) Private bucket. No policies on storage.objects for it: only the server (service key) can
--    read or write. The app serves each photo through /api/contractor/jobs/<job>/photos/<id>/img
--    after checking the company.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('job-photos', 'job-photos', false, 6000000, array['image/jpeg', 'image/png', 'image/webp'])
on conflict (id) do update
  set public = false,
      file_size_limit = excluded.file_size_limit,
      allowed_mime_types = excluded.allowed_mime_types;
