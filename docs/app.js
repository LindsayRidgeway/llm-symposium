document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const globalSearchInput = document.getElementById('globalSearchInput');
  const clearSearchBtn = document.getElementById('clearSearchBtn');
  const searchFeedback = document.getElementById('searchFeedback');
  const searchResultCount = document.getElementById('searchResultCount');
  const searchQueryText = document.getElementById('searchQueryText');
  const themeToggle = document.getElementById('themeToggle');
  const articleCards = document.querySelectorAll('.article-card');
  const navLinks = document.querySelectorAll('.nav-link');

  // Calculator Elements
  const portalSource = document.getElementById('portalSource');
  const portalCodec = document.getElementById('portalCodec');
  const portalHours = document.getElementById('portalHours');
  const calcSourceRate = document.getElementById('calcSourceRate');
  const calcBtRate = document.getElementById('calcBtRate');
  const calcMonthlyGB = document.getElementById('calcMonthlyGB');
  const calcAssessment = document.getElementById('calcAssessment');
  const calcNotes = document.getElementById('calcNotes');

  // --- 1. THEME SWITCHER ---
  const savedTheme = localStorage.getItem('symposium_theme') || 'dark';
  if (savedTheme === 'light') {
    document.body.classList.remove('dark-theme');
    document.body.classList.add('light-theme');
    updateThemeToggleLabel(true);
  }

  function updateThemeToggleLabel(isLight) {
    if (!themeToggle) return;
    const icon = themeToggle.querySelector('.theme-icon');
    const label = themeToggle.querySelector('.theme-label');
    if (isLight) {
      icon.textContent = '🌙';
      label.textContent = 'Dark';
    } else {
      icon.textContent = '☀️';
      label.textContent = 'Light';
    }
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const isLight = document.body.classList.toggle('light-theme');
      document.body.classList.toggle('dark-theme', !isLight);
      localStorage.setItem('symposium_theme', isLight ? 'light' : 'dark');
      updateThemeToggleLabel(isLight);
    });
  }

  // --- 2. GLOBAL REAL-TIME SEARCH ---
  function executeSearch() {
    const query = globalSearchInput.value.trim().toLowerCase();
    let matches = 0;

    if (query.length > 0) {
      clearSearchBtn.style.display = 'block';
      searchFeedback.style.display = 'block';
      searchQueryText.textContent = query;
    } else {
      clearSearchBtn.style.display = 'none';
      searchFeedback.style.display = 'none';
    }

    articleCards.forEach(card => {
      const text = card.textContent.toLowerCase();
      if (query === '' || text.includes(query)) {
        card.style.display = 'block';
        matches++;
      } else {
        card.style.display = 'none';
      }
    });

    if (query.length > 0) {
      searchResultCount.textContent = matches;
    }
  }

  if (globalSearchInput) {
    globalSearchInput.addEventListener('input', executeSearch);

    clearSearchBtn.addEventListener('click', () => {
      globalSearchInput.value = '';
      executeSearch();
      globalSearchInput.focus();
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === '/' && document.activeElement !== globalSearchInput) {
        e.preventDefault();
        globalSearchInput.focus();
      } else if (e.key === 'Escape' && document.activeElement === globalSearchInput) {
        globalSearchInput.value = '';
        executeSearch();
        globalSearchInput.blur();
      }
    });
  }

  // --- 3. NAV LINK SMOOTH SCROLL & ACTIVE STATE ---
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      if (href && href.startsWith('#')) {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          navLinks.forEach(l => l.classList.remove('active'));
          link.classList.add('active');
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });
  });

  // --- 4. CALCULATOR ENGINE ---
  const sourceTable = {
    '48_24': { rate: 2304, compression: 0.65, name: 'Lossless (24/48)', optimal: true },
    '44_16': { rate: 1411, compression: 0.60, name: 'CD (16/44.1)', optimal: true },
    '96_24': { rate: 4608, compression: 0.70, name: 'Hi-Res (24/96)', optimal: false },
    '192_24': { rate: 9216, compression: 0.75, name: 'Hi-Res (24/192)', optimal: false },
    'spotify': { rate: 320, compression: 1.0, name: 'Spotify 320k', optimal: false }
  };

  const codecTable = {
    'ldac_adaptive': { name: 'LDAC Adaptive', typ: 660, isLdac: true },
    'ldac_990': { name: 'LDAC 990k', typ: 990, isLdac: true },
    'ldac_660': { name: 'LDAC 660k', typ: 660, isLdac: true },
    'aptx_hd': { name: 'aptX HD', typ: 576, isLdac: false },
    'aac': { name: 'AAC Android', typ: 256, isLdac: false },
    'sbc': { name: 'SBC Standard', typ: 328, isLdac: false }
  };

  function updatePortalCalculator() {
    if (!portalSource || !portalCodec || !portalHours) return;

    const src = sourceTable[portalSource.value];
    const codec = codecTable[portalCodec.value];
    const hours = parseFloat(portalHours.value) || 2;

    const streamKbps = portalSource.value === 'spotify' ? 320 : Math.round(src.rate * src.compression);
    const monthlyGB = ((streamKbps * 3600 * hours * 30) / (8 * 1000 * 1000)).toFixed(1);

    calcSourceRate.textContent = `${src.rate.toLocaleString()} kbps`;
    calcBtRate.textContent = `${codec.name} (~${codec.typ} kbps)`;
    calcMonthlyGB.textContent = `~${monthlyGB} GB / mo`;

    if (portalSource.value === '192_24' || portalSource.value === '96_24') {
      calcAssessment.textContent = 'Wasteful Bandwidth (Downsampled)';
      calcAssessment.className = 'stat-value status-sub';
      calcNotes.innerHTML = `⚠️ <strong>Hi-Res Mismatch:</strong> Your phone downloads a massive <strong>${src.rate} kbps</strong> stream, then discards >75% of sample packets to compress into Bluetooth bandwidth. Set Apple Music to <strong>Lossless (24-bit/48kHz)</strong> for the exact same acoustic output using 1/4 the data.`;
    } else if (portalSource.value === 'spotify') {
      calcAssessment.textContent = 'Lossy Source Bottleneck';
      calcAssessment.className = 'stat-value status-sub';
      calcNotes.innerHTML = `⚠️ <strong>Lossy Source:</strong> Spotify sends lossy 320 kbps Vorbis audio. LDAC transmits it cleanly, but can never restore lost transient master data.`;
    } else if (portalCodec.value === 'ldac_adaptive' || portalCodec.value === 'ldac_660') {
      calcAssessment.textContent = 'Optimal Golden Balance';
      calcAssessment.className = 'stat-value status-opt';
      calcNotes.innerHTML = `✅ <strong>Acoustically Transparent:</strong> Bit-perfect 24-bit/48kHz ALAC lossless cleanly streams through LDAC adaptive bandwidth with zero packet dropouts or micro-stutters.`;
    } else if (portalCodec.value === 'ldac_990') {
      calcAssessment.textContent = 'High Resolution (RF Jitter Risk)';
      calcAssessment.className = 'stat-value status-sub';
      calcNotes.innerHTML = `⚡ <strong>Max Bitrate:</strong> Superb lab fidelity, but prone to micro-stuttering under 2.4GHz Wi-Fi congestion or phone-in-pocket conditions.`;
    } else {
      calcAssessment.textContent = 'Codec Bottleneck';
      calcAssessment.className = 'stat-value status-sub';
      calcNotes.innerHTML = `⚠️ <strong>Limited Wireless Codec:</strong> Standard AAC/SBC limits dynamics and transient response. Use an LDAC-certified receiver for near-lossless clarity.`;
    }
  }

  if (portalSource && portalCodec && portalHours) {
    portalSource.addEventListener('change', updatePortalCalculator);
    portalCodec.addEventListener('change', updatePortalCalculator);
    portalHours.addEventListener('input', updatePortalCalculator);
    updatePortalCalculator();
  }
});
