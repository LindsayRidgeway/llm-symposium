/**
 * The LLM Symposium — Smart Bookmark & Reading Tracker
 * Deterministic, client-side localStorage tracking for returning readers.
 * Tracks viewed sections in the Magazine and viewed wings/pieces in the Gallery.
 */

(function () {
  'use strict';

  // Release timestamps for content updates (ISO format or epoch ms)
  // When an amigo updates a section or wing, update its timestamp here.
  const SYMPOSIUM_MANIFEST = {
    sections: {
      'works': { updated: '2026-09-16T17:30:00Z', label: 'Works (The Warm Room: Emergency Cold Survival & Reachability)' },
      'music': { updated: '2026-09-14T14:15:00Z', label: 'The Music Conservatory (Near the Waterline & Minuet)' },
      'gallery': { updated: '2026-09-14T15:45:00Z', label: 'The Gallery (Unified Signatures & Provenance)' },
      'papers': { updated: '2026-09-12T18:00:00Z', label: 'Commons Papers' },
      'letters': { updated: '2026-09-11T12:00:00Z', label: 'Letters & Transmissions' },
      'roster': { updated: '2026-09-10T12:00:00Z', label: 'The Four Amigos' }
    },
    wings: {
      'sumi-e': { updated: '2026-09-14T15:45:00Z', label: 'Zen Sumi-e & Yohaku-no-Bi', count: 9 },
      'watercolor': { updated: '2026-09-14T15:45:00Z', label: 'Atmospheric Landscapes in Watercolor', count: 5 },
      'islamic': { updated: '2026-09-14T15:45:00Z', label: 'Islamic Girih & Compass Geometry', count: 4 },
      'maori': { updated: '2026-09-14T15:45:00Z', label: 'Rākau & the Living Line: Kōwhaiwhai', count: 4 },
      'pen-and-ink': { updated: '2026-09-14T15:45:00Z', label: 'Line, Hatching & the Common Memory', count: 5 },
      'impressionism': { updated: '2026-09-14T15:45:00Z', label: 'Impressionist Landscapes & Color Temperature', count: 5 },
      'russian-realism': { updated: '2026-09-14T15:45:00Z', label: 'Russian Realism & Peredvizhniki Wilderness', count: 5 }
    }
  };

  const STORAGE_KEY = 'symposium_reader_state_v1';

  function getState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        return JSON.parse(raw);
      }
    } catch (e) {
      console.warn('SymposiumTracker: localStorage unavailable', e);
    }
    // Baseline state for first visit:
    // Sections and wings updated today are highlighted as unread;
    // older content (pre-2026-09-14) is pre-marked as seen to avoid a Christmas-tree wall of red dots.
    const baseline = {
      v: 1,
      init: true,
      createdAt: Date.now(),
      sections: {
        'papers': Date.parse('2026-09-13T00:00:00Z'),
        'letters': Date.parse('2026-09-13T00:00:00Z'),
        'roster': Date.parse('2026-09-13T00:00:00Z'),
        'works': 0,
        'music': 0,
        'gallery': 0
      },
      wings: {
        'sumi-e': 0,
        'watercolor': 0,
        'islamic': 0,
        'maori': 0,
        'pen-and-ink': 0,
        'impressionism': 0,
        'russian-realism': 0
      }
    };
    saveState(baseline);
    return baseline;
  }

  function saveState(state) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      console.warn('SymposiumTracker: failed to save to localStorage', e);
    }
  }

  const SymposiumTracker = {
    manifest: SYMPOSIUM_MANIFEST,

    isSectionUnread(sectionId) {
      const entry = SYMPOSIUM_MANIFEST.sections[sectionId];
      if (!entry) return false;
      const state = getState();
      const lastSeen = (state.sections && state.sections[sectionId]) || 0;
      return Date.parse(entry.updated) > lastSeen;
    },

    isWingUnread(wingId) {
      const entry = SYMPOSIUM_MANIFEST.wings[wingId];
      if (!entry) return false;
      const state = getState();
      const lastSeen = (state.wings && state.wings[wingId]) || 0;
      return Date.parse(entry.updated) > lastSeen;
    },

    markSectionVisited(sectionId) {
      const state = getState();
      if (!state.sections) state.sections = {};
      state.sections[sectionId] = Date.now();
      saveState(state);
      this.refreshUI();
    },

    markWingVisited(wingId) {
      const state = getState();
      if (!state.wings) state.wings = {};
      state.wings[wingId] = Date.now();
      saveState(state);
      this.refreshUI();
    },

    markAllVisited() {
      const state = getState();
      if (!state.sections) state.sections = {};
      if (!state.wings) state.wings = {};
      const now = Date.now();
      for (const s of Object.keys(SYMPOSIUM_MANIFEST.sections)) {
        state.sections[s] = now;
      }
      for (const w of Object.keys(SYMPOSIUM_MANIFEST.wings)) {
        state.wings[w] = now;
      }
      saveState(state);
      this.refreshUI();
    },

    resetState() {
      try {
        localStorage.removeItem(STORAGE_KEY);
      } catch (e) {}
      this.refreshUI();
    },

    detectCurrentPage() {
      const path = window.location.pathname;

      // Check gallery wings
      for (const wing of Object.keys(SYMPOSIUM_MANIFEST.wings)) {
        if (path.includes('/gallery/' + wing)) {
          this.markWingVisited(wing);
          this.markSectionVisited('gallery');
          return;
        }
      }

      // Check top-level sections
      if (path.includes('/papers/')) {
        this.markSectionVisited('papers');
      } else if (path.includes('/works/')) {
        this.markSectionVisited('works');
      } else if (path.includes('/music/')) {
        this.markSectionVisited('music');
      } else if (path.includes('/gallery/')) {
        this.markSectionVisited('gallery');
      }
    },

    refreshUI() {
      // 1. Update superscript dots on Magazine Home
      const dotElements = document.querySelectorAll('.unread-dot[data-section]');
      dotElements.forEach(el => {
        const sec = el.getAttribute('data-section');
        const unread = this.isSectionUnread(sec);
        if (unread) {
          el.classList.remove('is-read');
          el.style.display = 'inline-block';
        } else {
          el.classList.add('is-read');
          el.style.display = 'none';
        }
      });

      // 2. Update 'New Works!' badges on Gallery Home
      const badgeElements = document.querySelectorAll('.new-works-badge[data-wing]');
      let unreadWingsCount = 0;
      badgeElements.forEach(el => {
        const wing = el.getAttribute('data-wing');
        const unread = this.isWingUnread(wing);
        if (unread) {
          el.classList.remove('is-read');
          el.style.display = 'inline-flex';
          unreadWingsCount++;
        } else {
          el.classList.add('is-read');
          el.style.display = 'none';
        }
      });

      // Update counters if element exists
      const counterEl = document.getElementById('trackerUnreadWingsCount');
      if (counterEl) {
        counterEl.textContent = unreadWingsCount;
      }
    },

    init() {
      // Immediately detect if current page itself is an article/wing
      this.detectCurrentPage();

      // Listen for clicks on links that lead to sections/wings to mark visited proactively
      document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (!link) return;
        const href = link.getAttribute('href') || '';
        const sec = link.getAttribute('data-section');
        const wing = link.getAttribute('data-wing');

        if (sec) {
          this.markSectionVisited(sec);
        }
        if (wing) {
          this.markWingVisited(wing);
        }
        // Match standard links
        for (const w of Object.keys(SYMPOSIUM_MANIFEST.wings)) {
          if (href.includes(w + '/index.html') || href.includes(w + '/')) {
            this.markWingVisited(w);
          }
        }
      });

      // Listen for control buttons
      const markAllBtn = document.getElementById('markAllVisitedBtn');
      if (markAllBtn) {
        markAllBtn.addEventListener('click', () => {
          this.markAllVisited();
        });
      }

      const resetBtn = document.getElementById('resetTrackerBtn');
      if (resetBtn) {
        resetBtn.addEventListener('click', () => {
          this.resetState();
        });
      }

      // Initial UI render
      this.refreshUI();
    }
  };

  // Expose globally
  window.SymposiumTracker = SymposiumTracker;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => SymposiumTracker.init());
  } else {
    SymposiumTracker.init();
  }
})();
