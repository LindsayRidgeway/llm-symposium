// Dmitri's question #3, answered with an instrument that cannot lose the evidence:
// every console message (any type), every non-GET request URL, every response status.
// A brand-new room, one exchange, nothing filtered.
const L = require('./lib2');
const TOPIC = process.argv[2] || 'Third room: does each of you get a copy of what is said here, in your own files?';
const REPO = 'https://api.github.com/repos/LindsayRidgeway/tribe-gwen';
(async () => {
  const { ctx, pg } = await L.open();
  pg.on('console', m => console.log('   [console.' + m.type() + '] ' + m.text().slice(0, 300)));
  pg.on('pageerror', e => console.log('   [pageerror] ' + String(e).slice(0, 300)));
  pg.on('request', r => {
    if (r.method() === 'GET') return;
    const u = r.url();
    if (!/api\.github\.com|dashscope|openrouter/.test(u)) return;
    console.log('   [req] ' + r.method() + ' ' + u.replace(REPO, '') + (/dashscope|openrouter/.test(u) ? ' (ENGINE)' : ''));
  });
  pg.on('response', async r => {
    const u = r.url();
    if (r.request().method() === 'GET') return;
    if (!/api\.github\.com|dashscope|openrouter/.test(u)) return;
    console.log('   [res] ' + r.status() + ' ' + u.replace(REPO, '').slice(0, 110) + (/dashscope|openrouter/.test(u) ? ' (ENGINE)' : ''));
  });

  await L.gotoRetry(pg, 'https://ai-tribe.netlify.app/#/table');
  await pg.waitForSelector('#topic', { timeout: 45000 });
  await L.settle(pg, 3000);
  const build = await pg.evaluate(() => (window.BUILD || document.body.innerHTML.match(/const BUILD = '[^']*'/) || ['?'])[0]);
  console.log('[build] ' + build);
  await L.fillSel(pg, 'topic', TOPIC);
  await pg.evaluate(() => [...document.querySelectorAll('input[type=checkbox]')].forEach(c => { if (!c.checked) c.click(); }));
  console.log('[checked all members]');
  await L.settle(pg, 800);
  await L.clickText(pg, 'Open it');
  const t0 = Date.now();
  while (Date.now() - t0 < 150000) {
    await L.settle(pg, 4000);
    if (/#\/c\//.test(pg.url()) && !(await L.modal(pg))) break;
  }
  console.log('[room open] ' + pg.url());
  await L.settle(pg, 4000);
  await pg.waitForSelector('#tsay', { timeout: 45000 });
  await pg.fill('#tsay', 'One line each: name one file of yours that a room turn should have written, and say whether it was written.');
  await pg.evaluate(() => document.querySelector('#tsend').click());
  console.log('[sent — holding the tab open, nothing filtered]');
  let last = '';
  for (let i = 0; i < 50; i++) {
    await L.settle(pg, 5000);
    const busy = await pg.evaluate(() => /writing…|asking|thinking…/.test(document.body.innerText));
    if ('busy=' + busy !== last) { console.log(`   [+${(i + 1) * 5}s] busy=` + busy); last = 'busy=' + busy; }
    if (!busy && i > 10) break;
  }
  console.log('[idle — holding 40s more for late writes]');
  await L.settle(pg, 40000);
  const s = await pg.evaluate(() => document.body.innerText);
  console.log('--- room tail ---');
  console.log(s.split('\n').filter(l => l.trim()).slice(-30).join('\n').slice(0, 2500));
  await L.shot(pg, '60-first-exchange');
  console.log('ROOM_URL=' + pg.url());
  await ctx.close();
})().catch(e => { console.error('ERR', e.stack || e.message); process.exit(1); });
