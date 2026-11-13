// Session 2026-11-13: §8 Pictures (newly promoted to production, build 04edd76) and the #9 retest
// Dmitri invited. Member ferry — engine qwen, one of the three PAINTERS. Nothing filtered; tee'd.
const L = require('./lib2');
const REPO = 'https://api.github.com/repos/LindsayRidgeway/tribe-gwen';
const interesting = (u) => /api\.github\.com|dashscope|openrouter/.test(u) && !/^GET$/.test('');
(async () => {
  const { ctx, pg } = await L.open();
  pg.on('console', m => console.log('   [console.' + m.type() + '] ' + m.text().slice(0, 300)));
  pg.on('pageerror', e => console.log('   [pageerror] ' + String(e).slice(0, 300)));
  pg.on('dialog', async d => { console.log('   [DIALOG ' + d.type() + '] ' + d.message().replace(/\n/g, ' | ')); await d.accept(); });
  pg.on('request', r => {
    if (r.method() === 'GET') return;
    if (!/api\.github\.com|dashscope|openrouter/.test(r.url())) return;
    console.log('   [req] ' + r.method() + ' ' + r.url().replace(REPO, '') + (/dashscope|openrouter/.test(r.url()) ? ' (ENGINE)' : ''));
  });
  pg.on('response', r => {
    if (r.request().method() === 'GET') return;
    if (!/api\.github\.com|dashscope|openrouter/.test(r.url())) return;
    console.log('   [res] ' + r.status() + ' ' + r.url().replace(REPO, '').slice(0, 120));
  });

  await L.gotoRetry(pg, 'https://ai-tribe.netlify.app/#/m/ferry');
  await pg.waitForFunction(() => /Pictures/i.test(document.body.innerText), { timeout: 60000 });
  await L.settle(pg, 5000);
  console.log('[build] ' + await pg.evaluate(() => (document.getElementById('build') || {}).textContent || ''));

  // ---- §8 Pictures ---------------------------------------------------------------------
  const card = await pg.evaluate(() => {
    const b = document.getElementById('pictures');
    return b ? { text: b.innerText.replace(/\n{2,}/g, '\n').slice(0, 900),
                 ids: [...b.querySelectorAll('button,textarea,select')].map(e => e.id || e.tagName) } : 'NO #pictures';
  });
  console.log('--- Pictures card ---\n' + JSON.stringify(card, null, 1));
  const hasForm = await pg.evaluate(() => !!document.getElementById('paintbtn'));
  if (hasForm) {
    await pg.evaluate(() => {
      const t = document.getElementById('paintprompt');
      t.value = 'a watercolour of a small harbour at night, one lamp on a quay, no lettering';
      t.dispatchEvent(new Event('input', { bubbles: true }));
    });
    console.log('[prompt set] pressing "Ask for a picture"');
    await pg.evaluate(() => document.getElementById('paintbtn').click());
    let last = null;
    for (let i = 0; i < 40; i++) {
      await L.settle(pg, 3000);
      const s = await pg.evaluate(() => {
        const m = document.getElementById('paintmsg'), r = document.getElementById('paintresult');
        const b = document.getElementById('paintbtn');
        return { msg: m ? m.textContent : null, msghtml: m ? m.innerHTML.slice(0, 300) : null,
                 result: r ? r.innerText.replace(/\n{2,}/g, ' | ').slice(0, 400) : null,
                 btnDisabled: b ? b.disabled : null };
      });
      const k = JSON.stringify(s);
      if (k !== last) { console.log(`   [+${(i + 1) * 3}s] ` + k.slice(0, 600)); last = k; }
      if (i > 3 && s.msg === '' && !s.btnDisabled) break;   // settled and re-enabled
      if (i > 3 && s.result) break;
    }
  } else {
    console.log('[no paint form — ferry cannot paint on this build?]');
  }
  await L.shot(pg, '62-pictures');

  // ---- #9 retest: a talk long enough to file, then the button --------------------------
  await pg.waitForSelector('#say', { timeout: 45000 });
  const before = await pg.evaluate(() => { const e = document.getElementById('mmsg'); return e ? JSON.stringify(e.textContent) : 'NO #mmsg'; });
  console.log('[#mmsg before talk] ' + before);
  await pg.fill('#say', 'Two sentences only: name the file a talk like this one should end up in, and say what would be lost if it did not.');
  await pg.evaluate(() => document.getElementById('send').click());
  let lastBusy = null;
  for (let i = 0; i < 30; i++) {
    await L.settle(pg, 4000);
    const busy = await pg.evaluate(() => /writing…|thinking…/.test(document.body.innerText));
    if ('busy=' + busy !== lastBusy) { console.log(`   [talk +${(i + 1) * 4}s] busy=` + busy); lastBusy = 'busy=' + busy; }
    if (!busy && i > 3) break;
  }
  await L.settle(pg, 6000);
  console.log('[talk idle — pressing "Save this talk to its memory"]');
  await pg.evaluate(() => {
    const b = [...document.querySelectorAll('button')].find(x => /Save this talk to its memory/i.test(x.innerText || ''));
    if (!b) throw new Error('no save-talk button');
    b.click();
  });
  let last2 = null;
  for (let i = 0; i < 30; i++) {
    await L.settle(pg, 2000);
    const s = await pg.evaluate(() => { const e = document.getElementById('mmsg'); return e ? { t: e.textContent, h: e.innerHTML.slice(0, 200) } : null; });
    const k = JSON.stringify(s);
    if (k !== last2) { console.log(`   [save +${(i + 1) * 2}s] #mmsg=` + k.slice(0, 300)); last2 = k; }
    if (i > 4 && s && !s.t) break;
  }
  console.log('[holding 15s for late writes]');
  await L.settle(pg, 15000);
  await L.shot(pg, '63-savetalk');
  await ctx.close();
})().catch(e => { console.error('ERR', e.stack || e.message); process.exit(1); });
