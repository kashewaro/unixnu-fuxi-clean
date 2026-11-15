# AGENTS.md — UniXNU-fuxi-clean

Clean Xiaomi 13 (fuxi, SM8550) bring-up on upstream UniXNU. Read this before changing anything.

## Hard rules

- `fastboot boot` ONLY. Never `fastboot flash` (until the userdata stage, with explicit approval).
- No forked dependencies: UniXNU + SoC feed are `UniXNU/*` upstream. Vendored driver sources only with `ORIGIN.md` + license.
- `board.example` must stay absent; `unixnu` refuses example boards.
- Secrets (chip-id, private keys) never enter git. Current builds use the `BRINGUP_SEED` constant — no secret needed.
- Every change lands in `porting.toml` evidence, or the record workflow fails.

## Evidence without camera

No camera/second phone: boot results are eye-read from the panel and transcribed by hand
(checkpoint lines, panic providers, probe tables — double-checked by a second boot).
Later: TWRP/ADB pulls of the persistent log region. Never invent lines you did not see.

## Commands (from upstream UniXNU checkout)

- `./unixnu defconfig fuxi_defconfig -D ../UniXNU-fuxi-clean`
- `./unixnu fetch -D ../UniXNU-fuxi-clean`
- `./unixnu status --json -D ../UniXNU-fuxi-clean`
- `./unixnu tree -D ../UniXNU-fuxi-clean`
- CI (`macos-26`): kernel → payload (`--unique-chip-id 0x0123456789abcdef`) → firmware (DEBUG) → bootimg → encrypted artifact.
- Decrypt: `bash ci/decrypt-boot-image.sh <private-key> <artifact-dir> <out-boot.img>`
