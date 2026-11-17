#!/usr/bin/env python3
"""Build build/verified-root-os-xnu-bundle/libVerifiedRootProbe.a for fuxi.

The owner-signed per-window policies (build/verified-root-os and
build/verified-root-systemos) are produced before the kernel build from the
staged original disk images (see the CI policy-signing steps); the kernel
bootstrap pass leaves the compile records this script replays. The bundle
carries the real verified-root policy, hash tables and XNU crypto bridge, and
its strong symbols override the weak stubs of package/FuxiUfsPolicyStub.cpp at
the final link, so NativeUfs validates published windows against the signed
policy. Without the signed policies this recipe refuses instead of linking
stubs.
"""

from pathlib import Path
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]   # the assembled build tree: scripts are copied into it
OUT = ROOT / 'build/verified-root-os-xnu-bundle'


def run(command, **kwargs):
    return subprocess.check_output([str(v) for v in command], timeout=900, **kwargs)


def require(value, message):
    if not value:
        raise SystemExit(message)


for directory in (ROOT / 'build/verified-root-os', ROOT / 'build/verified-root-systemos'):
    require((directory / 'manifest.bin').is_file() and (directory / 'verification.json').is_file()
            and (directory / 'trusted-key.bin').is_file(),
            f'{directory.relative_to(ROOT)} missing: sign the owner policies before the kernel build')
require((ROOT / '.cache/firmware/target-volumes/044-76034-038.dmg').is_file(),
        '.cache/firmware/target-volumes/044-76034-038.dmg missing: stage the original SystemOS disk image')
record = ROOT / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/bsd/DEVELOPMENT/bsd_init.o.json'
require(record.is_file(), f'{record.relative_to(ROOT)} missing: the bootstrap pass must leave compile records')

# The probe bundle layout build-verified-root-probe.py --include-systemos reads
# (on case-insensitive macOS verified-root-systemos IS verified-root-SystemOS).
sys_dir = ROOT / 'build/verified-root-systemos'
sys_dir.mkdir(parents=True, exist_ok=True)
src_manifest = ROOT / 'build/verified-root-SystemOS/manifest.bin'
dst_manifest = sys_dir / 'manifest.bin'
if not (dst_manifest.exists() and os.path.samefile(src_manifest, dst_manifest)):
    shutil.copyfile(src_manifest, dst_manifest)
policies = ROOT / 'build/verified-root-policies/SystemOS'
shutil.copyfile(policies / 'verification.json', sys_dir / 'verification.json')
shutil.copyfile(policies / 'trusted-key.bin', sys_dir / 'trusted-key.bin')

# The bsd_init compile record references ios-obj/EXPORT_HDRS/libsa, which only
# obj/EXPORT_HDRS creates; the header is unneeded for these sources, but the
# probe compiles with -Werror.
(ROOT / 'build/xnu/ios-obj/EXPORT_HDRS/libsa').mkdir(parents=True, exist_ok=True)

run([sys.executable, str(ROOT / 'scripts/build-verified-root-probe.py'),
     '--component', 'os', '--include-systemos'], cwd=ROOT)
archive = OUT / 'libVerifiedRootProbe.a'
require(archive.is_file(), f'{archive.relative_to(ROOT)} missing after the probe build')
print(f'verified-root probe bundle: {archive.relative_to(ROOT)}')
