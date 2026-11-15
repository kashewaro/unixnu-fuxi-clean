# Origin of the touch stack

- `drivers/FuxiFtsTouch/` — unchanged copy of `OddlyLabs/FuxiFtsTouch`
  (ST FTM5 protocol + contact tracking + host tests), via
  `kashewaro/unixnu-fuxi`. BSD-2-Clause-Patent, see `drivers/FuxiFtsTouch/LICENSE`.
- `package/FuxiTouchProbe.cpp`, `package/FuxiHidProbe.cpp`,
  `package/FuxiTouchBoard.h`, `package/TouchBoard.h`, `package/QcomRpmh.c`,
  `package/QcomRpmh.h` — fuxi board glue from `kashewaro/unixnu-fuxi`
  (itself derived from `UniXNU-sheng`, see file headers).
- `package/NativeHidInput.cpp` — unchanged copy of UniXNU `ShengHidInput`
  (see `scripts/fuxi_hid_abi.py` for the pinned kernelcache addresses).
- `scripts/build-fuxi-touch.py`, `scripts/build-fuxi-hid-input.py`,
  `scripts/fuxi_hid_abi.py`, `patches/xnu/fuxi-touch-probe.patch`,
  `tests/board_test.c`, `ci/check-hid-bindings.py` — from
  `kashewaro/unixnu-fuxi`.
- `drivers/FuxiFtsTouch/Test/`, `drivers/FuxiFtsTouch/README.md`,
  `drivers/FuxiFtsTouch/AGENTS.md` — upstream docs/tests, unchanged.
