document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const searchInput = document.getElementById('searchInput');
  const clearSearch = document.getElementById('clearSearch');
  const filterPills = document.querySelectorAll('.pill');
  const articles = document.querySelectorAll('.card');
  const searchSummary = document.getElementById('searchSummary');
  const matchCount = document.getElementById('matchCount');
  const searchTermDisplay = document.getElementById('searchTermDisplay');
  const themeToggle = document.getElementById('themeToggle');
  const copyPromptBtn = document.getElementById('copyPromptBtn');
  const innerCopyBtn = document.getElementById('innerCopyBtn');
  const toast = document.getElementById('toast');

  // Calculator Elements
  const calcSource = document.getElementById('calcSource');
  const calcCodec = document.getElementById('calcCodec');
  const calcHours = document.getElementById('calcHours');
  const resSourceRate = document.getElementById('resSourceRate');
  const resBtRate = document.getElementById('resBtRate');
  const resMonthlyData = document.getElementById('resMonthlyData');
  const resVerdict = document.getElementById('resVerdict');
  const resExplanation = document.getElementById('resExplanation');

  let currentCategory = 'all';

  // --- 1. SEARCH & FILTER LOGIC ---
  function filterAndSearch() {
    const query = searchInput.value.trim().toLowerCase();
    let visibleCount = 0;

    if (query.length > 0) {
      clearSearch.style.display = 'block';
    } else {
      clearSearch.style.display = 'none';
    }

    articles.forEach(article => {
      const category = article.getAttribute('data-category');
      const text = article.textContent.toLowerCase();
      const matchesCategory = (currentCategory === 'all' || category === currentCategory);
      const matchesQuery = (query === '' || text.includes(query));

      if (matchesCategory && matchesQuery) {
        article.style.display = 'block';
        visibleCount++;
      } else {
        article.style.display = 'none';
      }
    });

    if (query.length > 0) {
      searchSummary.style.display = 'block';
      matchCount.textContent = visibleCount;
      searchTermDisplay.textContent = query;
    } else {
      searchSummary.style.display = 'none';
    }
  }

  searchInput.addEventListener('input', filterAndSearch);

  clearSearch.addEventListener('click', () => {
    searchInput.value = '';
    filterAndSearch();
    searchInput.focus();
  });

  // Keyboard shortcut: '/' to focus search, 'Escape' to clear
  document.addEventListener('keydown', (e) => {
    if (e.key === '/' && document.activeElement !== searchInput) {
      e.preventDefault();
      searchInput.focus();
    } else if (e.key === 'Escape' && document.activeElement === searchInput) {
      searchInput.value = '';
      filterAndSearch();
      searchInput.blur();
    }
  });

  // Pill click handlers
  filterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      filterPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      currentCategory = pill.getAttribute('data-filter');
      filterAndSearch();
    });
  });

  // --- 2. CALCULATOR LOGIC ---
  const sourceSpecs = {
    '48_24': { name: 'Lossless 24-bit / 48 kHz ALAC', kbps: 2304, compressionFactor: 0.65, ideal: true },
    '44_16': { name: 'Standard CD 16-bit / 44.1 kHz', kbps: 1411, compressionFactor: 0.60, ideal: true },
    '96_24': { name: 'Hi-Res Lossless 24-bit / 96 kHz', kbps: 4608, compressionFactor: 0.70, ideal: false },
    '192_24': { name: 'Extreme Hi-Res 24-bit / 192 kHz', kbps: 9216, compressionFactor: 0.75, ideal: false },
    'spotify': { name: 'Spotify Ogg Vorbis 320 kbps', kbps: 320, compressionFactor: 1.0, ideal: false }
  };

  const codecSpecs = {
    'ldac_adaptive': { name: 'LDAC Adaptive (Best Effort)', maxKbps: 990, typKbps: 660, isLdac: true },
    'ldac_990': { name: 'LDAC 990 kbps (Locked)', maxKbps: 990, typKbps: 990, isLdac: true },
    'ldac_660': { name: 'LDAC 660 kbps (Balanced)', maxKbps: 660, typKbps: 660, isLdac: true },
    'ldac_330': { name: 'LDAC 330 kbps (Connectivity)', maxKbps: 330, typKbps: 330, isLdac: true },
    'aptx_hd': { name: 'aptX HD', maxKbps: 576, typKbps: 576, isLdac: false },
    'aac': { name: 'AAC (Android default)', maxKbps: 256, typKbps: 256, isLdac: false },
    'sbc': { name: 'SBC Standard', maxKbps: 328, typKbps: 328, isLdac: false }
  };

  function updateCalculator() {
    const srcKey = calcSource.value;
    const codecKey = calcCodec.value;
    const hours = parseFloat(calcHours.value) || 2;

    const src = sourceSpecs[srcKey];
    const codec = codecSpecs[codecKey];

    // Calculate effective cellular download stream rate
    const downloadKbps = srcKey === 'spotify' ? 320 : Math.round(src.kbps * src.compressionFactor);
    
    // Monthly data in GB: (kbps * 3600 * hours * 30) / (8 * 1,000,000)
    const monthlyGB = ((downloadKbps * 3600 * hours * 30) / (8 * 1000 * 1000)).toFixed(1);

    resSourceRate.textContent = `${src.kbps.toLocaleString()} kbps (Uncompressed)`;
    resBtRate.textContent = `${codec.name} ~${codec.typKbps} kbps`;
    resMonthlyData.textContent = `~${monthlyGB} GB / mo`;

    // Verdict & Explanation
    if (srcKey === '192_24' || srcKey === '96_24') {
      resVerdict.textContent = 'Data Inefficient (Bandwidth Wasted)';
      resVerdict.className = 'res-val status-warn';
      resExplanation.innerHTML = `⚠️ <strong>Hi-Res Bandwidth Mismatch:</strong> Your phone is downloading a massive <strong>${src.kbps} kbps</strong> stream over cellular/Wi-Fi, but Bluetooth LDAC tops out at <strong>990 kbps</strong>. Over 75% of downloaded sample packets are permanently discarded before wireless transmission. Switch source to <strong>Lossless (24-bit / 48 kHz)</strong> for identical audible fidelity with 1/4 the data consumption.`;
    } else if (srcKey === 'spotify') {
      resVerdict.textContent = 'Source Bottleneck (Lossy)';
      resVerdict.className = 'res-val status-warn';
      resExplanation.innerHTML = `⚠️ <strong>Lossy Source:</strong> Spotify transmits compressed 320 kbps Vorbis files. While LDAC can stream it cleanly, you are re-encoding an already lossy stream. Apple Music's lossless ALAC tier delivers bit-perfect masters at the same subscription cost.`;
    } else if (codecKey === 'ldac_adaptive' || codecKey === 'ldac_660') {
      resVerdict.textContent = 'Golden Configuration (Acoustically Transparent)';
      resVerdict.className = 'res-val status-good';
      resExplanation.innerHTML = `✅ <strong>Optimal Audiophile Balance:</strong> Bit-perfect 24-bit/48kHz source audio is dynamically packaged by LDAC with seamless adaptive fallback to eliminate stutters while preserving transient speed and micro-detail.`;
    } else if (codecKey === 'ldac_990') {
      resVerdict.textContent = 'High Quality (RF Stutter Risk)';
      resVerdict.className = 'res-val status-warn';
      resExplanation.innerHTML = `⚡ <strong>Max Bitrate Locked:</strong> Excellent lab fidelity, but subject to buffer dropouts in high-interference 2.4GHz Wi-Fi environments. If you hear micro-skips, switch to <em>Best Effort (Adaptive)</em>.`;
    } else {
      resVerdict.textContent = 'Sub-Optimal Bluetooth Codec';
      resVerdict.className = 'res-val status-warn';
      resExplanation.innerHTML = `⚠️ <strong>Codec Bottleneck:</strong> ${codec.name} caps transmission bandwidth below high-fidelity thresholds, compressing dynamic transients. Switch to an LDAC-compatible receiver.`;
    }
  }

  calcSource.addEventListener('change', updateCalculator);
  calcCodec.addEventListener('change', updateCalculator);
  calcHours.addEventListener('input', updateCalculator);
  updateCalculator();

  // --- 3. THEME TOGGLE ---
  const currentTheme = localStorage.getItem('theme') || 'dark';
  if (currentTheme === 'light') {
    document.body.classList.remove('dark-theme');
    document.body.classList.add('light-theme');
    updateThemeButton(true);
  }

  function updateThemeButton(isLight) {
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

  themeToggle.addEventListener('click', () => {
    const isLight = document.body.classList.toggle('light-theme');
    document.body.classList.toggle('dark-theme', !isLight);
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
    updateThemeButton(isLight);
  });

  // --- 4. CLIPBOARD COPY ---
  function showToast(msg = 'Copied to clipboard!') {
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 2400);
  }

  function copyRAGPrompt() {
    const text = document.getElementById('ragContextBlock').innerText;
    navigator.clipboard.writeText(text).then(() => {
      showToast('RAG Prompt Block Copied!');
    }).catch(err => {
      console.error('Failed to copy: ', err);
    });
  }

  copyPromptBtn.addEventListener('click', copyRAGPrompt);
  innerCopyBtn.addEventListener('click', copyRAGPrompt);
});
