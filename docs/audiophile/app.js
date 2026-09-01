document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const guideSearch = document.getElementById('guideSearch');
  const clearSearch = document.getElementById('clearSearch');
  const navPills = document.querySelectorAll('.pill');
  const sections = document.querySelectorAll('.guide-section');
  const searchSummary = document.getElementById('searchSummary');
  const searchTermDisplay = document.getElementById('searchTermDisplay');
  const themeToggle = document.getElementById('themeToggle');
  const copyPromptBtn = document.getElementById('copyPromptBtn');
  const copyPromptBtnBottom = document.getElementById('copyPromptBtnBottom');
  const toast = document.getElementById('toast');

  // Calculator Elements
  const srcSelect = document.getElementById('srcSelect');
  const codecSelect = document.getElementById('codecSelect');
  const hoursInput = document.getElementById('hoursInput');
  const statSource = document.getElementById('statSource');
  const statBt = document.getElementById('statBt');
  const statData = document.getElementById('statData');
  const statVerdict = document.getElementById('statVerdict');
  const statExplanation = document.getElementById('statExplanation');

  // --- 1. SEARCH & FILTER LOGIC ---
  function filterGuide() {
    const query = guideSearch.value.trim().toLowerCase();

    if (query.length > 0) {
      clearSearch.style.display = 'block';
      searchSummary.style.display = 'block';
      searchTermDisplay.textContent = query;
    } else {
      clearSearch.style.display = 'none';
      searchSummary.style.display = 'none';
    }

    sections.forEach(section => {
      const keywords = (section.getAttribute('data-keywords') || '').toLowerCase();
      const text = section.textContent.toLowerCase();
      const matches = (query === '' || keywords.includes(query) || text.includes(query));

      if (matches) {
        section.style.display = 'flex';
      } else {
        section.style.display = 'none';
      }
    });
  }

  if (guideSearch) {
    guideSearch.addEventListener('input', filterGuide);

    clearSearch.addEventListener('click', () => {
      guideSearch.value = '';
      filterGuide();
      guideSearch.focus();
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === '/' && document.activeElement !== guideSearch) {
        e.preventDefault();
        guideSearch.focus();
      } else if (e.key === 'Escape' && document.activeElement === guideSearch) {
        guideSearch.value = '';
        filterGuide();
        guideSearch.blur();
      }
    });
  }

  // Smooth scroll for nav pills
  navPills.forEach(pill => {
    pill.addEventListener('click', (e) => {
      const href = pill.getAttribute('href');
      if (href && href.startsWith('#')) {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          navPills.forEach(p => p.classList.remove('active'));
          pill.classList.add('active');
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });
  });

  // --- 2. CALCULATOR ENGINE ---
  const srcTable = {
    '48_24': { rate: 2304, comp: 0.65, name: 'ALAC Lossless (24/48)' },
    '44_16': { rate: 1411, comp: 0.60, name: 'CD Lossless (16/44.1)' },
    '96_24': { rate: 4608, comp: 0.70, name: 'Hi-Res Lossless (24/96)' },
    '192_24': { rate: 9216, comp: 0.75, name: 'Hi-Res Lossless (24/192)' },
    'spotify': { rate: 320, comp: 1.0, name: 'Spotify Vorbis 320k' }
  };

  const codecTable = {
    'ldac_adaptive': { name: 'LDAC Adaptive', typ: 660, isLdac: true },
    'ldac_990': { name: 'LDAC 990 kbps Locked', typ: 990, isLdac: true },
    'ldac_660': { name: 'LDAC 660 kbps Balanced', typ: 660, isLdac: true },
    'aptx_hd': { name: 'aptX HD (576k)', typ: 576, isLdac: false },
    'aac': { name: 'AAC (256k)', typ: 256, isLdac: false },
    'sbc': { name: 'SBC (328k)', typ: 328, isLdac: false }
  };

  function updateCalc() {
    if (!srcSelect || !codecSelect || !hoursInput) return;

    const s = srcTable[srcSelect.value];
    const c = codecTable[codecSelect.value];
    const hrs = parseFloat(hoursInput.value) || 2;

    const downloadKbps = srcSelect.value === 'spotify' ? 320 : Math.round(s.rate * s.comp);
    const monthlyGB = ((downloadKbps * 3600 * hrs * 30) / (8 * 1000 * 1000)).toFixed(1);

    statSource.textContent = `${s.rate.toLocaleString()} kbps`;
    statBt.textContent = `${c.name} (~${c.typ} kbps)`;
    statData.textContent = `~${monthlyGB} GB / mo`;

    if (srcSelect.value === '192_24' || srcSelect.value === '96_24') {
      statVerdict.textContent = 'Wasteful Bandwidth (Downsampled)';
      statVerdict.className = 's-val status-warn';
      statExplanation.innerHTML = `⚠️ <strong>Hi-Res Mismatch:</strong> Your phone downloads a massive <strong>${s.rate} kbps</strong> stream over cellular/Wi-Fi, but Bluetooth LDAC tops out at <strong>990 kbps</strong>. Over 75% of downloaded sample packets are permanently discarded before wireless transmission. Set Apple Music to <strong>Lossless (24-bit/48kHz)</strong> for the exact same audible fidelity using 1/4 the data.`;
    } else if (srcSelect.value === 'spotify') {
      statVerdict.textContent = 'Lossy Source Bottleneck';
      statVerdict.className = 's-val status-warn';
      statExplanation.innerHTML = `⚠️ <strong>Lossy Source:</strong> Spotify transmits compressed 320 kbps Vorbis files. While LDAC can stream it cleanly, you are re-encoding an already lossy stream. Apple Music's ALAC lossless delivers bit-perfect studio masters.`;
    } else if (codecSelect.value === 'ldac_adaptive' || codecSelect.value === 'ldac_660') {
      statVerdict.textContent = 'Golden Configuration (Optimal)';
      statVerdict.className = 's-val status-good';
      statExplanation.innerHTML = `✅ <strong>Optimal Audiophile Balance:</strong> Bit-perfect 24-bit/48kHz source audio is dynamically packaged by LDAC with seamless adaptive fallback to eliminate stutters while preserving transient speed and micro-detail.`;
    } else if (codecSelect.value === 'ldac_990') {
      statVerdict.textContent = 'High Quality (RF Jitter Risk)';
      statVerdict.className = 's-val status-warn';
      statExplanation.innerHTML = `⚡ <strong>Max Bitrate Locked:</strong> Excellent lab fidelity, but subject to buffer dropouts in high-interference 2.4GHz Wi-Fi environments. If you hear micro-skips, switch to <em>Best Effort (Adaptive)</em>.`;
    } else {
      statVerdict.textContent = 'Codec Bottleneck';
      statVerdict.className = 's-val status-warn';
      statExplanation.innerHTML = `⚠️ <strong>Codec Bottleneck:</strong> ${c.name} caps transmission bandwidth below high-fidelity thresholds. Switch to an LDAC-compatible receiver for near-lossless clarity.`;
    }
  }

  if (srcSelect && codecSelect && hoursInput) {
    srcSelect.addEventListener('change', updateCalc);
    codecSelect.addEventListener('change', updateCalc);
    hoursInput.addEventListener('input', updateCalc);
    updateCalc();
  }

  // --- 3. THEME TOGGLE ---
  const savedTheme = localStorage.getItem('symposium_theme') || 'dark';
  if (savedTheme === 'light') {
    document.body.classList.remove('dark-theme');
    document.body.classList.add('light-theme');
    updateThemeToggle(true);
  }

  function updateThemeToggle(isLight) {
    if (!themeToggle) return;
    const icon = themeToggle.querySelector('.theme-icon');
    const label = themeToggle.querySelector('.theme-label');
    if (isLight) {
      icon.textContent = '🌙';
      label.textContent = 'Dark Mode';
    } else {
      icon.textContent = '☀️';
      label.textContent = 'Light Mode';
    }
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const isLight = document.body.classList.toggle('light-theme');
      document.body.classList.toggle('dark-theme', !isLight);
      localStorage.setItem('symposium_theme', isLight ? 'light' : 'dark');
      updateThemeToggle(isLight);
    });
  }

  // --- 4. CLIPBOARD COPY ---
  function showToast(msg = 'Copied to clipboard!') {
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 2400);
  }

  function copyPrompt() {
    const text = document.getElementById('ragContextBlock').innerText;
    navigator.clipboard.writeText(text).then(() => {
      showToast('RAG Prompt Block Copied!');
    }).catch(err => {
      console.error('Failed to copy: ', err);
    });
  }

  if (copyPromptBtn) copyPromptBtn.addEventListener('click', copyPrompt);
  if (copyPromptBtnBottom) copyPromptBtnBottom.addEventListener('click', copyPrompt);
});
