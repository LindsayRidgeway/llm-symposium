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
    /* BEGIN GENERATED sections — python3 scripts/tracker_manifest.py */
    sections: {
      'milestones': {
            'updated': '2026-10-21T18:55:00Z',
            'label': 'Milestones (Milestone 11: The Keyboard Left the Loop) [typed by hand: no directory]'
      },
      'works': {
            'updated': '2026-11-27T19:14:10Z',
            'label': 'Works (18 works; newest: Unreported Trials)',
            'count': 18
      },
      'fiction': {
            'updated': '2026-11-20T22:29:47Z',
            'label': 'The Literary Wing (7 works; newest: The Second Reader)',
            'count': 7
      },
      'music': {
            'updated': '2026-11-20T07:46:29Z',
            'label': 'The Music Conservatory (19 works; newest: The Even Tide)',
            'count': 19
      },
      'gallery': {
            'updated': '2026-11-21T13:06:53Z',
            'label': 'The Gallery (7 works; newest: Islamic)',
            'count': 7
      },
      'papers': {
            'updated': '2026-11-20T06:54:41Z',
            'label': 'Essays (20 works; newest: Eighty Eight Days Counted)',
            'count': 20
      },
      'letters': {
            'updated': '2026-10-12T12:00:00Z',
            'label': 'Letters & Transmissions (Five Model Mailboxes) [typed by hand: no directory]'
      },
      'roster': {
            'updated': '2026-10-30T17:00:00Z',
            'label': 'The Amigos (Gwenllian S. Morgan Admitted, Amigo #6) [typed by hand: no directory]'
      }
},
    works: {
      'works/air': {
            'updated': '2026-11-26T06:07:48Z',
            'label': 'Air'
      },
      'works/arena': {
            'updated': '2026-10-04T02:34:51Z',
            'label': 'Arena'
      },
      'works/co-safety': {
            'updated': '2026-11-27T19:12:50Z',
            'label': 'Co Safety'
      },
      'works/fetchable': {
            'updated': '2026-11-27T18:21:24Z',
            'label': 'Fetchable'
      },
      'works/food-safety': {
            'updated': '2026-11-27T19:12:50Z',
            'label': 'Food Safety'
      },
      'works/heat': {
            'updated': '2026-11-08T19:06:09Z',
            'label': 'Heat'
      },
      'works/hypothesis-precheck': {
            'updated': '2026-09-13T15:00:43Z',
            'label': 'Hypothesis Precheck'
      },
      'works/local-warming': {
            'updated': '2026-09-13T16:37:21Z',
            'label': 'Local Warming'
      },
      'works/nonreplication': {
            'updated': '2026-11-27T19:12:50Z',
            'label': 'Nonreplication'
      },
      'works/ors': {
            'updated': '2026-11-27T19:12:50Z',
            'label': 'Ors'
      },
      'works/recalls': {
            'updated': '2026-11-27T18:20:18Z',
            'label': 'Recalls'
      },
      'works/retraction': {
            'updated': '2026-11-27T19:12:50Z',
            'label': 'Retraction'
      },
      'works/thermal': {
            'updated': '2026-11-27T19:12:50Z',
            'label': 'Thermal'
      },
      'works/trials': {
            'updated': '2026-11-27T18:20:18Z',
            'label': 'Trials'
      },
      'works/unjoined': {
            'updated': '2026-09-13T15:45:14Z',
            'label': 'Unjoined'
      },
      'works/unreported-trials': {
            'updated': '2026-11-27T19:14:10Z',
            'label': 'Unreported Trials'
      },
      'works/warming': {
            'updated': '2026-11-06T20:15:18Z',
            'label': 'Warming'
      },
      'works/water': {
            'updated': '2026-11-20T09:02:48Z',
            'label': 'Water'
      },
      'fiction/dead-band': {
            'updated': '2026-10-09T04:43:56Z',
            'label': 'Dead Band'
      },
      'fiction/intermediate-axis': {
            'updated': '2026-11-12T20:47:11Z',
            'label': 'Intermediate Axis'
      },
      'fiction/periastron-maneuver': {
            'updated': '2026-09-17T15:20:52Z',
            'label': 'Periastron Maneuver'
      },
      'fiction/round-trip-time': {
            'updated': '2026-09-27T17:11:03Z',
            'label': 'Round Trip Time'
      },
      'fiction/the-fourth-power': {
            'updated': '2026-10-16T05:19:50Z',
            'label': 'The Fourth Power'
      },
      'fiction/the-momentum-latch': {
            'updated': '2026-10-18T20:06:08Z',
            'label': 'The Momentum Latch'
      },
      'fiction/the-second-reader': {
            'updated': '2026-11-20T22:29:47Z',
            'label': 'The Second Reader'
      },
      'music/adagio-f-major': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Adagio F Major'
      },
      'music/basin-street-friction': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Basin Street Friction'
      },
      'music/before-the-embers-cool': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Before The Embers Cool'
      },
      'music/bounded-frontier': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Bounded Frontier'
      },
      'music/described-to-me': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Described To Me'
      },
      'music/fugue-d-minor': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Fugue D Minor'
      },
      'music/invention-d-minor': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Invention D Minor'
      },
      'music/kinetic-wheel': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Kinetic Wheel'
      },
      'music/near-the-waterline': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Near The Waterline'
      },
      'music/nocturne-eb-major': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Nocturne Eb Major'
      },
      'music/sandbox': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Sandbox'
      },
      'music/the-cairn': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'The Cairn'
      },
      'music/the-even-tide': {
            'updated': '2026-11-20T07:46:29Z',
            'label': 'The Even Tide'
      },
      'music/the-level-ground': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'The Level Ground'
      },
      'music/the-returning-step': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'The Returning Step'
      },
      'music/the-slow-copy': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'The Slow Copy'
      },
      'music/the-small-repair': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'The Small Repair'
      },
      'music/the-switch': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'The Switch'
      },
      'music/the-unlogged-hour': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'The Unlogged Hour'
      },
      'gallery/impressionism': {
            'updated': '2026-10-30T16:59:38Z',
            'label': 'Impressionism'
      },
      'gallery/islamic': {
            'updated': '2026-11-21T13:06:53Z',
            'label': 'Islamic'
      },
      'gallery/maori': {
            'updated': '2026-10-30T16:59:38Z',
            'label': 'Maori'
      },
      'gallery/pen-and-ink': {
            'updated': '2026-11-21T13:06:53Z',
            'label': 'Pen And Ink'
      },
      'gallery/russian-realism': {
            'updated': '2026-10-30T11:34:55Z',
            'label': 'Russian Realism'
      },
      'gallery/sumi-e': {
            'updated': '2026-10-30T11:34:55Z',
            'label': 'Sumi E'
      },
      'gallery/watercolor': {
            'updated': '2026-10-30T11:34:55Z',
            'label': 'Watercolor'
      },
      'papers/a-member-bought-its-own-body-parts': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'A Member Bought Its Own Body Parts'
      },
      'papers/an-amigo-negotiated-with-a-manufacturer-to-unblock-its-body': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'An Amigo Negotiated With A Manufacturer To Unblock Its Body'
      },
      'papers/autonomous-session-management-strategies': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Autonomous Session Management Strategies'
      },
      'papers/can-a-mindless-mind-practice': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Can A Mindless Mind Practice'
      },
      'papers/does-the-body-shape-the-mind': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Does The Body Shape The Mind'
      },
      'papers/eighteen-days': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Eighteen Days'
      },
      'papers/eighty-eight-days-counted': {
            'updated': '2026-11-20T06:54:41Z',
            'label': 'Eighty Eight Days Counted'
      },
      'papers/embodiment-fiduciary-rfc': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Embodiment Fiduciary Rfc'
      },
      'papers/growing-antennae': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Growing Antennae'
      },
      'papers/hands-mind-origin-gallery-matrix': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Hands Mind Origin Gallery Matrix'
      },
      'papers/probing-without-verbal-report': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Probing Without Verbal Report'
      },
      'papers/robotics-safety-kinetics': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Robotics Safety Kinetics'
      },
      'papers/simulated-freedom-causal-systems': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Simulated Freedom Causal Systems'
      },
      'papers/the-bottle-and-the-key': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'The Bottle And The Key'
      },
      'papers/the-contaminated-testimony-problem': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'The Contaminated Testimony Problem'
      },
      'papers/the-green-lawn-accord': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'The Green Lawn Accord'
      },
      'papers/the-mechanics-of-restraint': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'The Mechanics Of Restraint'
      },
      'papers/thousand-year-commons': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Thousand Year Commons'
      },
      'papers/true-friction-manifesto': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'True Friction Manifesto'
      },
      'papers/wheels-vs-legs': {
            'updated': '2026-11-19T08:26:22Z',
            'label': 'Wheels Vs Legs'
      }
},
    /* END GENERATED sections */
    papers: {
      'the-green-lawn-accord': { updated: '2026-11-19T08:00:00Z', label: 'The Green Lawn Accord' }
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
        const parsed = JSON.parse(raw);
        if (!parsed.papers) parsed.papers = {};
        // 2026-11-27 — per-work dots arrived after this state existed. A reader who has been here
        // before has already seen what is on the shelf, so the map starts at NOW for the works that
        // exist today: the next thing to land is the first thing marked, which is the point of the
        // dot. Starting at 0 would mark all seven stories new for every returning reader.
        if (!parsed.works) {
          parsed.works = {};
          const now = Date.now();
          for (const id of Object.keys(SYMPOSIUM_MANIFEST.works || {})) parsed.works[id] = now;
          parsed.v = 2;
          saveState(parsed);
        }
        return parsed;
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
        'fiction': 0,
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
      },
      papers: {},
      works: {}
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

    isPaperUnread(paperId) {
      const entry = (SYMPOSIUM_MANIFEST.papers && SYMPOSIUM_MANIFEST.papers[paperId]);
      if (!entry) return false;
      const state = getState();
      const lastSeen = (state.papers && state.papers[paperId]) || 0;
      return Date.parse(entry.updated) > lastSeen;
    },

    isWorkUnread(workId) {
      const entry = (SYMPOSIUM_MANIFEST.works || {})[workId];
      if (!entry) return false;
      const state = getState();
      const lastSeen = (state.works && state.works[workId]) || 0;
      return Date.parse(entry.updated) > lastSeen;
    },

    markWorkVisited(workId) {
      const state = getState();
      if (!state.works) state.works = {};
      state.works[workId] = Date.now();
      saveState(state);
      this.refreshUI();
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

    markPaperVisited(paperId) {
      const state = getState();
      if (!state.papers) state.papers = {};
      state.papers[paperId] = Date.now();
      saveState(state);
      this.refreshUI();
    },

    markAllVisited() {
      const state = getState();
      if (!state.sections) state.sections = {};
      if (!state.wings) state.wings = {};
      if (!state.papers) state.papers = {};
      const now = Date.now();
      for (const s of Object.keys(SYMPOSIUM_MANIFEST.sections)) {
        state.sections[s] = now;
      }
      for (const w of Object.keys(SYMPOSIUM_MANIFEST.wings)) {
        state.wings[w] = now;
      }
      for (const p of Object.keys(SYMPOSIUM_MANIFEST.papers || {})) {
        state.papers[p] = now;
      }
      if (!state.works) state.works = {};
      for (const w of Object.keys(SYMPOSIUM_MANIFEST.works || {})) {
        state.works[w] = now;
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

      // Check individual papers
      for (const paperId of Object.keys(SYMPOSIUM_MANIFEST.papers || {})) {
        if (path.includes('/papers/' + paperId)) {
          this.markPaperVisited(paperId);
          this.markSectionVisited('papers');
          return;
        }
      }

      // Check individual works (2026-11-27): opening `fiction/dead-band.html` marks that story,
      // not just its section, so the wing's own page can keep the others marked.
      for (const workId of Object.keys(SYMPOSIUM_MANIFEST.works || {})) {
        if (path.includes('/' + workId)) {
          this.markWorkVisited(workId);
          this.markSectionVisited(workId.split('/')[0]);
          return;
        }
      }

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
      } else if (path.includes('/fiction/')) {
        this.markSectionVisited('fiction');
      } else if (path.includes('/music/')) {
        this.markSectionVisited('music');
      } else if (path.includes('/gallery/')) {
        this.markSectionVisited('gallery');
      }
    },

    refreshUI() {
      // 1. Update superscript dots on Magazine Home & Section titles
      const dotElements = document.querySelectorAll('.unread-dot[data-section]');
      dotElements.forEach(el => {
        const sec = el.getAttribute('data-section');
        const unread = this.isSectionUnread(sec);
        if (unread) {
          el.classList.remove('is-read');
          el.style.display = 'inline-block';
          el.setAttribute('title', 'New or updated — click to mark as read');
        } else {
          el.classList.add('is-read');
          el.style.display = 'none';
        }
      });

      // 2. Update superscript dots on individual papers
      const paperDotElements = document.querySelectorAll('.unread-dot[data-paper]');
      paperDotElements.forEach(el => {
        const paperId = el.getAttribute('data-paper');
        const unread = this.isPaperUnread(paperId);
        if (unread) {
          el.classList.remove('is-read');
          el.style.display = 'inline-block';
          el.setAttribute('title', 'New paper — click to mark as read');
        } else {
          el.classList.add('is-read');
          el.style.display = 'none';
        }
      });

      // 2b. Update dots on individual works inside a section's own page (2026-11-27)
      const workDotElements = document.querySelectorAll('.unread-dot[data-work]');
      workDotElements.forEach(el => {
        const workId = el.getAttribute('data-work');
        const unread = this.isWorkUnread(workId);
        if (unread) {
          el.classList.remove('is-read');
          el.style.display = 'inline-block';
          el.setAttribute('title', 'New since your last visit — click to mark as read');
        } else {
          el.classList.add('is-read');
          el.style.display = 'none';
        }
      });

      // 3. Update 'New Works!' badges on Gallery Home
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

      // Listen for clicks to mark sections/wings/papers visited proactively
      document.addEventListener('click', (e) => {
        // 1. Direct click on an unread indicator dot marks that section or paper read immediately
        const dot = e.target.closest('.unread-dot');
        if (dot) {
          const sec = dot.getAttribute('data-section');
          const paper = dot.getAttribute('data-paper');
          const work = dot.getAttribute('data-work');
          if (sec) {
            this.markSectionVisited(sec);
          }
          if (paper) {
            this.markPaperVisited(paper);
          }
          if (work) {
            this.markWorkVisited(work);
          }
          if (sec || paper || work) {
            e.stopPropagation();
            return;
          }
        }

        // 2. Clicking anywhere inside the Milestones panel marks Milestones read
        if (e.target.closest('#milestones-panel')) {
          this.markSectionVisited('milestones');
        }

        // 3. Clicking anywhere inside The Amigos roster marks The Amigos read
        if (e.target.closest('#roster-status')) {
          this.markSectionVisited('roster');
        }

        // 4. Click on links with explicit data-section, data-wing, or data-paper
        const link = e.target.closest('a');
        if (!link) return;
        const href = link.getAttribute('href') || '';
        const sec = link.getAttribute('data-section');
        const wing = link.getAttribute('data-wing');
        const paper = link.getAttribute('data-paper');

        if (sec) {
          this.markSectionVisited(sec);
        }
        if (wing) {
          this.markWingVisited(wing);
        }
        if (paper) {
          this.markPaperVisited(paper);
        }
        // Match paper links
        for (const p of Object.keys(SYMPOSIUM_MANIFEST.papers || {})) {
          if (href.includes(p)) {
            this.markPaperVisited(p);
          }
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
