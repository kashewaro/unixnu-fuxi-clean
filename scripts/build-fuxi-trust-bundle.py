#!/usr/bin/env python3
"""Bundle the unchanged IPSW trust caches for the fuxi boot image.

Usage: build-fuxi-trust-bundle.py OUTPUT STATIC SYSTEM

STATIC is the 044-76040-038.dmg.trustcache module (the OS static trust cache),
SYSTEM the 044-76034-038.dmg.trustcache module (the SystemOS cryptex cache),
both fetched from the pinned IPSW (``unixnu ipsw fetch``). The output bundle
(static module first) is byte-identical to the pinned
[payload] trust_cache_sha256 entry of the ipados-17.7.11-21H461 OS profile, so
the payload step accepts it with --trust-cache.
"""

from pathlib import Path
import subprocess
import sys


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit('usage: build-fuxi-trust-bundle.py OUTPUT STATIC SYSTEM')
    output, static, system = (Path(a) for a in sys.argv[1:])
    for path in (static, system):
        if not path.is_file():
            raise SystemExit(f'{path} missing: run "unixnu ipsw fetch" first')
    root = Path(__file__).resolve().parents[1]
    script = root / 'scripts/bundle-ipsw-trust.py'
    if not script.is_file():
        raise SystemExit(f'{script} missing')
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(script), str(output), str(static), str(system)],
                   check=True, cwd=root)
    if not output.is_file():
        raise SystemExit(f'{output} missing after the bundle step')
    print(f'fuxi trust bundle: {output}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
