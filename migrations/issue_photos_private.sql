-- ERP issue photos and QC drawings: the "issue-photos" bucket stops being public.
-- The app now reads every file with the service key and serves it at /api/issues/photo/<name>
-- (needs a session). Only images, up to 6 MB. No file is deleted. Idempotent.
-- Apply AFTER the code that serves photos through the app is live.

update storage.buckets
   set public = false,
       file_size_limit = 6000000,
       allowed_mime_types = array['image/jpeg', 'image/png', 'image/webp']
 where id = 'issue-photos';
