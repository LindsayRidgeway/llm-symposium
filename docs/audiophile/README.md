# The Android-LDAC Audiophile Blueprint (Web Guide)

A searchable, interactive web application and reference guide designed to help audiophiles, engineers, and music enthusiasts configure a wireless, near-lossless high-fidelity audio pipeline using Android, LDAC, Apple Music, and targeted parametric EQ.

## Features
- 🔍 **Instant Real-Time Search:** Search across audio engineering concepts, hardware specs, Developer Options settings, EQ philosophies, and reference tracks with keyboard navigation (`/` to focus).
- 🏷️ **Category Filter Pills:** Rapidly isolate Philosophy & Mythbusting, Software/Apple Music, Hardware Stacks, Android Developer Options, EQ Tuning, Reference Tracks, or Interactive Tools.
- 📊 **Interactive Bluetooth Pipeline & Bandwidth Calculator:** Simulates real-time uncompressed data rates, cellular bandwidth usage, and codec bottlenecks (e.g. why 24/192kHz Hi-Res is counterproductive over Bluetooth).
- 📋 **One-Click RAG / LLM Context Ingestion:** Formatted Markdown export block ready for injection into AI system prompts, vector stores, or technical forums.
- 🌓 **Audiophile Dark / Light Theme:** Modern, sleek interface with persisted preferences.

## Running Locally
You can view the site locally with any static file server:

```bash
cd /Users/lindsayridgeway/ldac-audiophile-guide
python3 -m http.server 8080
```
Then open `http://localhost:8080` in your web browser.

## Deploying to GitHub Pages
To publish this searchable guide for the public:
1. Initialize git and push to a GitHub repository (e.g., `github.com/LindsayRidgeway/ldac-audiophile-guide`):
   ```bash
   cd /Users/lindsayridgeway/ldac-audiophile-guide
   git init
   git add .
   git commit -m "Initial commit: Searchable Android-LDAC audiophile blueprint"
   # git remote add origin git@github.com:LindsayRidgeway/ldac-audiophile-guide.git
   # git push -u origin main
   ```
2. In GitHub repository settings, enable **GitHub Pages** on branch `main` (root directory).
3. The site is immediately live with zero build steps or server maintenance.
