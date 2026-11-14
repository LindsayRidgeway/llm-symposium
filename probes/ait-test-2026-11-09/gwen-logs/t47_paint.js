// §8 Pictures, tested for real: paint.yml + lab/paint.py copied unmodified into tribe-gwen
// (commit 360f12c) so the button can reach its machinery. Member ferry, engine qwen, one of the three
// PAINTERS. Key: TRIBE_API_KEY_QWEN (my DashScope key, set by me on 2026-11-10).
const L = require('./lib2');
const REPO = 'https://api.github.com/repos/LindsayRidgeway/tribe-gwen';
(async () => {
  const { ctx, pg } = await L.open();
  pg.on('console', m => console.log('   [console.' + m.type() + '] ' + m.text().slice(0, 300)));
  pg.on('pageerror', e => console.log('   [pageerror] ' + String(e).slice(0, 300)));
  pg.on('dialog', async d => { console.log('   [DIALOG ' + d.type() + '] ' + d.message().replace(/\n/g, ' | ')); await d.accept(); });
  pg.on('request', r => {
    if (r.method() === 'GET') return;
    if (!/api\.github\.com/.test(r.url())) return;
    console.log('   [req] ' + r.method() + ' ' + r.url().replace(REPO, ''));
  });
  pg.on('response', r => {
    if (r.request().method() === 'GET') return;
    if (!/api\.github\.com/.test(r.url())) return;
    console.log('   [res] ' + r.status() + ' ' + r.url().replace(REPO, '').slice(0, 120));
  });

  await L.gotoRetry(pg, 'https://ai-tribe.netlify.app/#/m/ferry');
  await pg.waitForSelector('#paintbtn', { timeout: 60000 });
  await L.settle(pg, 3000);
  console.log('[build] ' + await pg.evaluate(() => (document.getElementById('build') || {}).textContent || ''));
  await pg.evaluate(() => {
    const t = document.getElementById('paintprompt');
    t.value = 'a watercolour of a small harbour at night, one lamp on a quay, no lettering';
    t.dispatchEvent(new Event('input', { bubbles: true }));
  });
  console.log('[pressing "Ask for a picture"]');
  await pg.evaluate(() => document.getElementById('paintbtn').click());
  let last = null;
  for (let i = 0; i < 110; i++) {            // up to ~5.5 min, matching the page's own 90-poll watch
    await L.settle(pg, 3000);
    const s = await pg.evaluate(() => {
      const m = document.getElementById('paintmsg'), r = document.getElementById('paintresult'),
            b = document.getElementById('paintbtn');
      return { msg: m ? m.textContent : null, result: r ? r.innerText.replace(/\n{2,}/g, ' | ').slice(0, 500) : null,
               btn: b ? b.disabled : null };
    });
    const k = JSON.stringify(s);
    if (k !== last) { console.log(`   [+${(i + 1) * 3}s] ` + k.slice(0, 700)); last = k; }
    if (s.result) break;
    if (i > 4 && s.btn === false && !s.msg) break;   // re-enabled with nothing said: a failure path
  }
  await L.settle(pg, 5000);
  const final = await pg.evaluate(() => {
    const r = document.getElementById('paintresult');
    return { html: r ? r.innerHTML.slice(0, 900) : null,
             img: r ? [...r.querySelectorAll('img')].map(i => ({ src: i.src.slice(0, 140), shown: i.style.display !== 'none' })) : [],
             msg: (document.getElementById('paintmsg') || {}).textContent };
  });
  console.log('--- final paint result ---\n' + JSON.stringify(final, null, 1));
  await L.shot(pg, '64-picture');
  await ctx.close();
})().catch(e => { console.error('ERR', e.stack || e.message); process.exit(1); });
