#!/usr/bin/env python3
"""Build build/fuxi-ufs/libFuxiUfs.a: probe-only UFS link inputs for fuxi.

The upstream ShengUfs component (built by its own recipe and force-loaded by
the kernel script when CONFIG_XNU_NATIVE_UFS=1) references three groups of
symbols this tree does not otherwise provide:

- the IOBlockStorageDevice base (vtable, constructor/destructor, methods):
  the BCM2837 source kernel does not compile IOKit storage, so this script
  assembles the pinned original imports
  (package/fuxi-storage-original-bindings.S, unchanged copy of SadNutWall's
  fuxi record for the unchanged iPadOS 17.7.11 kernelcache) as absolute
  symbols. No duplicate class is linked; at runtime they are the same
  addresses the prelinked Apple IOStorageFamily kext provides.
- the owner-verified block policy (verified_root_*, vr_*): the signed per
  window policy bundle is a Task 7 product. package/FuxiUfsPolicyStub.cpp
  defines an empty row, a zero count, an all-zero key and refusing entry
  points; configureVerification returns on the zero count, so verification
  is disabled rather than approximated and the probe never reaches that path.
- the passive boot-progress observer: a no-op definition (never called by
  the probe; the observer contract forbids blocking or transport access).

Link order matters: this archive is force-loaded after libShengUfs.a (see
CONFIG_XNU_EXTRA_LD_ARCHIVES), so its definitions satisfy the driver's
references.
"""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]   # the assembled build tree: scripts are copied into it
OUT = ROOT / 'build/fuxi-ufs'
OUT.mkdir(parents=True, exist_ok=True)
KIT = ROOT / 'kits/fuxi'


def run(command, **kwargs):
    return subprocess.check_output([str(v) for v in command], timeout=180, **kwargs)


def require(value, message):
    if not value:
        raise SystemExit(message)


bindings = ROOT / 'kits/fuxi/fuxi-storage-original-bindings.S'
require(bindings.is_file(), f'{bindings} missing: vendor SadNutWall fuxi-storage-original-bindings.S')
stub = KIT / 'FuxiUfsPolicyStub.cpp'
require(stub.is_file(), f'{stub} missing')
for header in (ROOT / 'kits/VerifiedRoot/include/verified_root.h',
               ROOT / 'drivers/VirtioMmioBlock/VerifiedBlockPolicy.h'):
    require(header.is_file(), f'{header} missing: select ShengUfs in board.toml [components]')

xcrun = shutil.which('xcrun')
require(xcrun, 'xcrun missing: the kernel step runs on macOS')
sdk = subprocess.check_output([xcrun, '--sdk', 'iphoneos', '--show-sdk-path'], text=True).strip()

bindings_obj = OUT / 'storage-original-bindings.o'
run([xcrun, 'clang', '-target', 'arm64-apple-ios17.0', '-isysroot', sdk,
     '-Werror', '-c', bindings, '-o', bindings_obj])
print(f'assembled {bindings.relative_to(ROOT)}')

stub_obj = OUT / 'FuxiUfsPolicyStub.o'
run([xcrun, 'clang++', '-target', 'arm64-apple-ios17.0', '-isysroot', sdk,
     '-O2', '-Werror', '-Wall', '-Wextra', '-mgeneral-regs-only',
     '-I', ROOT / 'kits/VerifiedRoot/include', '-I', ROOT / 'drivers/VirtioMmioBlock',
     '-c', stub, '-o', stub_obj])
print(f'compiled {stub.relative_to(ROOT)}')

archive = OUT / 'libFuxiUfs.a'
archive.unlink(missing_ok=True)
run([xcrun, 'ar', 'rcs', archive, bindings_obj, stub_obj])

report = {
    'bindings_sha256': hashlib.sha256(bindings.read_bytes()).hexdigest(),
    'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
}
(OUT / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n')
print(f'probe-only UFS link inputs: {archive.relative_to(ROOT)}')
