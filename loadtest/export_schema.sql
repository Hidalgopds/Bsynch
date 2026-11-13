-- Run in the PRODUCTION project's SQL Editor. It only READS the structure (tables, columns,
-- keys, indexes, RLS, functions) and returns it as one block of SQL. No data rows are read.
-- Copy the result (column "ddl") and run it in the STAGING project's SQL Editor.
with t as (
  select c.oid, c.relname from pg_class c join pg_namespace n on n.oid = c.relnamespace
  where n.nspname = 'public' and c.relkind = 'r'
),
seqs as (
  select string_agg(format('create sequence if not exists public.%I;', s.relname), E'\n') x
  from pg_class s join pg_namespace n on n.oid = s.relnamespace where n.nspname = 'public' and s.relkind = 'S'
),
cols as (
  select t.relname, string_agg(format('  %I %s%s%s', a.attname, format_type(a.atttypid, a.atttypmod),
           case when d.adbin is not null then ' default ' || pg_get_expr(d.adbin, d.adrelid) else '' end,
           case when a.attnotnull then ' not null' else '' end), E',\n' order by a.attnum) c
  from t join pg_attribute a on a.attrelid = t.oid and a.attnum > 0 and not a.attisdropped
  left join pg_attrdef d on d.adrelid = t.oid and d.adnum = a.attnum
  group by t.relname
),
cons as (
  select t.relname, string_agg(format('  constraint %I %s', co.conname, pg_get_constraintdef(co.oid)), E',\n') c
  from t join pg_constraint co on co.conrelid = t.oid where co.contype in ('p', 'u', 'c') group by t.relname
),
tbl as (
  select string_agg(format(E'create table if not exists public.%I (\n%s%s\n);', cols.relname, cols.c,
                           coalesce(E',\n' || cons.c, '')), E'\n' order by cols.relname) x
  from cols left join cons using (relname)
),
fks as (
  select string_agg(format('alter table public.%I add constraint %I %s;', t.relname, co.conname, pg_get_constraintdef(co.oid)), E'\n') x
  from t join pg_constraint co on co.conrelid = t.oid where co.contype = 'f'
),
idx as (
  select string_agg(regexp_replace(i.indexdef, '^CREATE (UNIQUE )?INDEX ', 'CREATE \1INDEX IF NOT EXISTS ') || ';', E'\n') x
  from pg_indexes i where i.schemaname = 'public' and i.indexname not in (select conname from pg_constraint)
),
rls as (select string_agg(format('alter table public.%I enable row level security;', relname), E'\n') x from t),
fns as (
  select string_agg(pg_get_functiondef(p.oid) || ';', E'\n') x
  from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public'
)
select concat_ws(E'\n\n',
  '-- BSynch schema (structure only, no data)',
  seqs.x, tbl.x, fks.x, idx.x, rls.x, fns.x,
  'revoke all on function public.security_self_check() from public, anon, authenticated;',
  'grant execute on function public.security_self_check() to service_role;') as ddl
from seqs, tbl, fks, idx, rls, fns;
