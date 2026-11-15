# UniXNU fuxi-clean (Xiaomi 13, SM8550 8/256)

Clean bring-up on **upstream** `UniXNU/UniXNU` — no forked dependencies.
The only non-upstream input is `uefi-fuxi` firmware (proven 8 GB map on this unit).

- OS profile: `ipados-17.7.11-21H461` (arm64 base for bring-up; arm64e later)
- Boot: `fastboot boot` only, nothing flashed (until the userdata stage)
- Build host: GitHub Actions `macos-26`; local: WSL2 Ubuntu 24.04
- Evidence without camera: eye-read checkpoints + TWRP/ADB pulls

Plan: `docs/superpowers/plans/2026-11-16-fuxi-clean-bringup.md` (in your checkout).
Progress: `docs/superpowers/plans/sdd-2026-11-16-fuxi-clean-bringup-progress.md`.
