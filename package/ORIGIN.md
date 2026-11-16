# Origin of the touch stack (vendored, no forked dependencies)

The FTM5 protocol sources live in package/FuxiFtsTouch/ (NOT drivers/):
upstream's tree assembly drops device-local driver modules that have no
catalog component, while the device package/ is always linked as kits/fuxi.
scripts/build-fuxi-touch.py reads them from there.

- `package/FuxiFtsTouch/` — unchanged copy of `OddlyLabs/FuxiFtsTouch`
  (ST FTM5 protocol + contact tracking + host tests), via
  `kashewaro/unixnu-fuxi`. BSD-2-Clause-Patent, see `package/FuxiFtsTouch/LICENSE`.
  (Nested `.github` CI of that repo dropped; our workflow runs the tests.)
- `package/FuxiTouchProbe.cpp`, `package/FuxiHidProbe.cpp`,
  `package/FuxiSysProbe.cpp`, `package/FuxiTouchBoard.h`,
  `package/FuxiPanelBoard.h`, `package/TouchBoard.h`, `package/QcomRpmh.c`,
  `package/QcomRpmh.h` — fuxi board glue from `kashewaro/unixnu-fuxi`
  (itself derived from `UniXNU-sheng`, see file headers).
- `package/NativeHidInput.cpp` — unchanged copy of UniXNU `ShengHidInput`
  (see `scripts/fuxi_hid_abi.py` for the pinned kernelcache addresses).
- `package/fuxi-storage-original-bindings.S` — unchanged copy of SadNutWall's
  fuxi record (pinned IOBlockStorageDevice imports for the unchanged iPadOS
  17.7.11 kernelcache); lets ShengUfs link without the live QEMU storage
  capture. BSD-2-Clause-Patent, see the file header.
- `package/FuxiUfsPolicyStub.cpp` — our probe-only VerifiedRoot stubs
  (empty policy, zero count, refusing entries, no-op progress observer).
- `drivers/ShengUfs/` — unchanged UniXNU/ShengUfs sources at the pinned
  component revision 99d8bcd, EXCEPT the fuxi dual-boot delta: RootLayout.h
  takes the wanted GPT partition name as a parameter (default "userdata"),
  NativeUfs.cpp sets it from the `native-ufs-partition` boot argument in
  `start()`. Without the argument behavior is identical to upstream.
  Rationale: `findRootLayout` hardcodes "userdata", which collides with the
  Android partition after carving; the carved "unixnu" partition needs
  `native-ufs-partition=unixnu`. BSD-2-Clause-Patent, see LICENSE.
- `scripts/build-fuxi-touch.py` (paths adapted to package/FuxiFtsTouch),
  `scripts/build-fuxi-hid-input.py`, `scripts/fuxi_hid_abi.py`,
  `patches/xnu/fuxi-touch-probe.patch`, `tests/board_test.c`,
  `ci/check-hid-bindings.py` — from `kashewaro/unixnu-fuxi`.
- `package/FuxiFtsTouch/Test/`, `package/FuxiFtsTouch/README.md`,
  `package/FuxiFtsTouch/AGENTS.md` — upstream docs/tests, unchanged.
