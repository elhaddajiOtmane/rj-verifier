# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-13

### Added
- **SheerID Verifier:** Automated verification using `k12` engine logic.
- **SheerID Generator:** Document generation (`.pdf` and `.png`) for teachers/students.
- **Dual Mode UI:** Seamless switching between Verifier and Generator tabs.
- **Engagement Features:**
  - **Social Lock:** "Follow to Unlock" overlay on first launch.
  - **Donation Nagtag:** "Buy me a coffee" prompt every 5 uses.
- **Automatic Updates:** Integration with `electron-updater` (scaffolded).
- **Persistent Config:** Settings and usage stats saved in `Documents/RJ Verifier/config.json`.
- **Backup System:** Automatic backup of generated files to `Documents/RJ Verifier/`.

### Fixed
- Resolved blank screen issues during development by disabling auto-DevTools.
- Fixed social links opening in internal Electron windows; now properly routed to system default browser.
- Polished overlay animations for smooth entry/exit.
