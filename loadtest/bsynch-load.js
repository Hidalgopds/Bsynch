// BSynch load test (k6). Read-only: it signs in and browses like a person, it never creates,
// sends or deletes anything.
//
//   k6 run -e BASE_URL=https://bsynch-staging.onrender.com -e LT_USERS="user1:pass1,user2:pass2" \
//          -e COMPANY=hicons -e PROFILE=load loadtest/bsynch-load.js
//
// PROFILE: smoke (1 person, 1 min) · load (up to 50 at once) · stress (up to 100) · spike (0 → 80 suddenly)
// Passwords only come from the command line or environment variables; never write them in this file.
import http from 'k6/http';
import { check, group, sleep, fail } from 'k6';
import { Trend } from 'k6/metrics';

const BASE = (__ENV.BASE_URL || '').replace(/\/+$/, '');
const COMPANY = (__ENV.COMPANY || 'hicons').toLowerCase();
const PROFILE = __ENV.PROFILE || 'smoke';

// Safety: production is never a load-test target (real users, real emails, security lockouts and alerts)
if (!BASE) fail('Set BASE_URL to the staging address (e.g. https://bsynch-staging.onrender.com)');
if (/(^|\.)bsynch\.com(:\d+)?$/i.test(BASE.replace(/^https?:\/\//, '').split('/')[0])) {
  fail('BASE_URL points to production (bsynch.com). Load tests only run against staging.');
}

const PROFILES = {
  smoke: [{ duration: '5s', target: 1 }, { duration: '55s', target: 1 }],
  load: [{ duration: '1m', target: 10 }, { duration: '2m', target: 25 }, { duration: '2m', target: 50 }, { duration: '1m', target: 0 }],
  stress: [{ duration: '1m', target: 25 }, { duration: '2m', target: 50 }, { duration: '2m', target: 100 }, { duration: '1m', target: 0 }],
  spike: [{ duration: '20s', target: 5 }, { duration: '10s', target: 80 }, { duration: '1m', target: 80 }, { duration: '30s', target: 0 }],
};
if (!PROFILES[PROFILE]) fail('PROFILE must be smoke, load, stress or spike');

export const options = {
  scenarios: { people: { executor: 'ramping-vus', startVUs: 0, stages: PROFILES[PROFILE], gracefulRampDown: '20s' } },
  thresholds: {
    http_req_failed: ['rate<0.01'],          // under 1% errors
    http_req_duration: ['p(95)<800'],        // 95% of requests under 0.8 s
    'screen_work_orders': ['p(95)<1500'],    // opening Work orders (page + its data) under 1.5 s
    checks: ['rate>0.99'],
  },
  setupTimeout: '2m',
  noCookiesReset: true,
};

const screenWorkOrders = new Trend('screen_work_orders', true);
const screenCalendar = new Trend('screen_calendar', true);
const screenJob = new Trend('screen_job', true);

function users() {
  const raw = __ENV.LT_USERS || (__ENV.LT_USER ? `${__ENV.LT_USER}:${__ENV.LT_PASS || ''}` : '');
  const list = raw.split(',').map((s) => s.trim()).filter(Boolean).map((s) => {
    const i = s.indexOf(':');
    return { user: s.slice(0, i), pass: s.slice(i + 1) };
  });
  if (!list.length) fail('Set LT_USERS="user:pass,..." (test accounts that exist only in staging)');
  return list;
}

// Each test account signs in ONCE here and every simulated person reuses a session. Signing in on
// every iteration would hit the app's own brute-force protection (10 tries per account, 30 per IP).
export function setup() {
  const sessions = [];
  for (const u of users()) {
    const jar = http.cookieJar();
    const r = http.post(`${BASE}/api/login`, JSON.stringify({ username: u.user, password: u.pass }),
      { headers: { 'Content-Type': 'application/json' }, jar });
    if (r.status !== 200) fail(`Sign-in failed for ${u.user}: ${r.status} ${String(r.body).slice(0, 120)}`);
    const c = jar.cookiesForURL(BASE).bsynch_session;
    if (!c || !c.length) fail(`No session cookie for ${u.user}`);
    sessions.push(c[0]);
  }
  return { sessions };
}

function api(path) {
  return http.get(`${BASE}${path}`, { headers: { 'X-Contractor-Company': COMPANY }, tags: { name: path.split('?')[0].replace(/[0-9a-f-]{20,}/g, ':id') } });
}

export default function (data) {
  const jar = http.cookieJar();
  jar.set(BASE, 'bsynch_session', data.sessions[(__VU - 1) % data.sessions.length]);

  let jobs = [];
  group('Work orders', () => {
    const t0 = Date.now();
    const page = http.get(`${BASE}/contractor/projects?company=${COMPANY}`, { tags: { name: 'page:work-orders' } });
    const me = api('/api/contractor/me');
    const projects = api('/api/contractor/projects');
    const list = api('/api/contractor/jobs');
    const folders = api(`/api/contractor/${COMPANY}/client-folders`);
    screenWorkOrders.add(Date.now() - t0);
    check(page, { 'work orders page 200': (r) => r.status === 200 });
    check(me, { 'me 200': (r) => r.status === 200 });
    check(projects, { 'projects 200': (r) => r.status === 200 });
    check(list, { 'jobs 200': (r) => r.status === 200 });
    check(folders, { 'folders 200': (r) => r.status === 200 });
    try { jobs = list.json() || []; } catch (e) { jobs = []; }
  });
  sleep(1 + Math.random() * 2);

  if (Array.isArray(jobs) && jobs.length) {
    const job = jobs[Math.floor(Math.random() * jobs.length)];
    group('Open a work order', () => {
      const t0 = Date.now();
      const steps = api(`/api/contractor/jobs/${job.id}/steps`);
      const photos = api(`/api/contractor/jobs/${job.id}/photos`);
      screenJob.add(Date.now() - t0);
      check(steps, { 'steps 200': (r) => r.status === 200 });
      check(photos, { 'photos 200': (r) => r.status === 200 });
    });
    sleep(1 + Math.random() * 2);
  }

  group('Calendar', () => {
    const month = new Date().toISOString().slice(0, 7);
    const t0 = Date.now();
    const cal = api(`/api/contractor/${COMPANY}/calendar?month=${month}`);
    screenCalendar.add(Date.now() - t0);
    check(cal, { 'calendar 200': (r) => r.status === 200 });
  });
  sleep(1 + Math.random() * 2);

  if (__ENV.MANAGER === '1') {
    group('Invoicing and dashboard (Managers)', () => {
      check(api(`/api/contractor/${COMPANY}/invoicing/jobs`), { 'invoicing 200': (r) => r.status === 200 });
      check(api(`/api/contractor/${COMPANY}/invoices`), { 'invoices 200': (r) => r.status === 200 });
      check(api(`/api/contractor/${COMPANY}/dashboard`), { 'dashboard 200': (r) => r.status === 200 });
    });
    sleep(1 + Math.random() * 2);
  }
}

export function handleSummary(data) {
  const m = data.metrics;
  const p95 = (k) => (m[k] && m[k].values['p(95)'] !== undefined ? `${Math.round(m[k].values['p(95)'])} ms` : '—');
  const lines = [
    `BSynch load test · profile ${PROFILE} · ${BASE}`,
    `Requests: ${m.http_reqs ? m.http_reqs.values.count : 0}  ·  errors: ${m.http_req_failed ? (m.http_req_failed.values.rate * 100).toFixed(2) : 0}%`,
    `95% of requests under: ${p95('http_req_duration')}`,
    `Open Work orders (95%): ${p95('screen_work_orders')}  ·  Open a job: ${p95('screen_job')}  ·  Calendar: ${p95('screen_calendar')}`,
    `Most people at once: ${m.vus_max ? m.vus_max.values.max : 0}`,
    '',
  ];
  return { stdout: lines.join('\n'), 'loadtest/last-summary.json': JSON.stringify(data, null, 2) };
}
