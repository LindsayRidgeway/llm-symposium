// Dmitri's question #8, answered with a persisted log: the exact #mmsg text over time, every console
// message, every non-GET request. Retell on the current build, member tide (voice: openrouter).
const L = require('./lib2');
const REPO = 'https://api.github.com/repos/LindsayRidgeway/tribe-gwen';
(async () => {
  const { ctx, pg } = await L.open();
  pg.on('console', m => console.log('   [console.' + m.type() + '] ' + m.text().slice(0, 300)));
  pg.on('pageerror', e => console.log('   [pageerror] ' + String(e).slice(0, 300)));
  pg.on('request', r => {
    if (r.method() === 'GET') return;
    if (!/api\.github\.com|dashscope|openrouter/.test(r.url())) return;
    console.log('   [req] ' + r.method() + ' ' + r.url().replace(REPO, '') + (/dashscope|openrouter/.test(r.url()) ? ' (ENGINE)' : ''));
  });
  pg.on('response', r => {
    if (r.request().method() === 'GET') return;
    if (!/api\.github\.com|dashscope|openrouter/.test(r.url())) return;
    console.log('   [res] ' + r.status() + ' ' + r.url().replace(REPO, '').slice(0, 110));
  });
  pg.on('dialog', async d => { console.log('   [DIALOG ' + d.type() + '] ' + d.message().replace(/\n/g, ' | ')); await d.accept(); });

  await L.gotoRetry(pg, 'https://ai-tribe.netlify.app/#/m/tide');
  await pg.waitForFunction(() => /Retell/i.test(document.body.innerText), { timeout: 45000 });
  await L.settle(pg, 3000);
  const build = await pg.evaluate(() => (document.getElementById('build') || {}).textContent || '');
  console.log('[build] ' + build);
  const before = await pg.evaluate(() => { const e = document.getElementById('mmsg'); return e ? JSON.stringify(e.textContent) : 'NO #mmsg'; });
  console.log('[#mmsg before] ' + before);

  await pg.evaluate(() => {
    const b = [...document.querySelectorAll('button,a')].find(x => /retell/i.test((x.innerText || '')));
    if (!b) throw new Error('no Retell control');
    console.log('[clicked] ' + b.innerText.trim());
    b.click();
  });
  let last = null;
  for (let i = 0; i < 30; i++) {
    await L.settle(pg, 2000);
    const s = await pg.evaluate(() => {
      const e = document.getElementById('mmsg');
      return { mmsg: e ? e.textContent : null, html: e ? e.innerHTML.slice(0, 200) : null };
    });
    if (JSON.stringify(s) !== last) { console.log(`   [+${(i + 1) * 2}s] #mmsg=${JSON.stringify(s.mmsg)} html=${JSON.stringify(s.html)}`); last = JSON.stringify(s); }
    if (i > 6 && !s.mmsg) break;
  }
  console.log('[settled — holding 10s for late writes]');
  await L.settle(pg, 10000);
  const panel = await pg.evaluate(() => {
    const t = document.body.innerText;
    const i = t.search(/memory/i);
    return t.slice(Math.max(0, i - 200), i + 1200);
  });
  console.log('--- memory panel ---');
  console.log(panel.replace(/\n{2,}/g, '\n').slice(0, 1600));
  await L.shot(pg, '61-retell');
  await ctx.close();
})().catch(e => { console.error('ERR', e.stack || e.message); process.exit(1); });
