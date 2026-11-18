#!/usr/bin/env python3
"""Continue past the Apple root-seal check instead of panicking.

Why an archive step and not a patch: two board patches already edit bsd_init.c (the touch probe and the
display probe), so a third hunks-based patch has to be regenerated whenever either moves the surrounding
lines. That failed twice in CI, at :943 and then at :957. The archive chain runs from board.toml
[kernel] archives after kernel.py applies the patch series, so this edits the file the series produced
and matches the statement itself rather than a line number.

The change is one statement: the FSIOC_KERNEL_ROOTAUTH failure stops being a panic and becomes a log
line. That gate only asks whether APFS recognises an Apple Image4 seal; it does not decide whether the
data was checked. NativeUfs authenticates every 4 KiB block against the owner's VerifiedRoot policy
before publishing the window, so a read of anything the owner did not sign still fails.
"""
import argparse
import os
import re
import sys
from pathlib import Path

ORIGINAL = 'panic("rootvp not authenticated after mounting");'

# The XNU source reads, with tabs shown as \t:
#
#   \t\t\tint autherr = VNOP_IOCTL(rootvnode, FSIOC_KERNEL_ROOTAUTH, NULL, 0, vfs_context_kernel());
#   \t\t\tif (autherr) {
#   \t\t\t\tpanic("rootvp not authenticated after mounting");
#   \t\t\t}
#
# The statement is replaced, not the surrounding block, so indentation is taken from the match itself
# rather than written into the pattern.
REPLACEMENT_HEAD = '''{indent}/*
{indent} * fuxi (Xiaomi 13): the root volume on the unixnu partition is sealed by the owner's
{indent} * VerifiedRoot policy, not by Apple Image4, so APFS answers this ioctl with an error even
{indent} * though every block was checked against the owner's signed hash table. Report it and
{indent} * continue instead of panicking: refusing to boot here would leave the storage bring-up
{indent} * untestable, and the volume is the one the owner signed. Lowering this gate does not make
{indent} * an unverified volume readable: NativeUfs authenticates every 4 KiB block against the
{indent} * policy before publishing it, so a read of anything the owner did not sign still fails.
{indent} */
{indent}printf("bsd_init: root volume is not Apple-sealed "
{indent}    "(FSIOC_KERNEL_ROOTAUTH returned %d); continuing on the owner policy\\n", autherr);'''


def locate() -> Path:
    """The patch series is applied to .cache/xnu-work inside the build tree this script runs in."""
    here = Path.cwd()
    candidates = []
    for name in ('UNIXNU_XNU_WORK', 'XNU_WORK'):
        value = os.environ.get(name)
        if value:
            candidates.append(Path(value))
    candidates += [here / '.cache/xnu-work', here / 'build/xnu-work']

    for candidate in candidates:
        source = candidate / 'bsd/kern/bsd_init.c'
        if source.is_file():
            return source
    tried = '\n  '.join(str(candidate / 'bsd/kern/bsd_init.c') for candidate in candidates)
    raise SystemExit(f'build-fuxi-root-auth: bsd_init.c not found; tried\n  {tried}')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('sources', nargs='*', help='ignored; board.toml entries stay uniform')
    args = parser.parse_args()
    del args.sources

    source = locate()
    text = source.read_text(encoding='utf-8')

    if 'continuing on the owner policy' in text:
        print(f'build-fuxi-root-auth: already applied in {source}')
        return 0

    if ORIGINAL not in text:
        raise SystemExit(f'build-fuxi-root-auth: {ORIGINAL} not found in {source}; the kernel source moved')

    # Match the panic line with its own indentation, and require the ROOTAUTH ioctl somewhere in the
    # sixty lines before it, so an unrelated panic with the same text is never rewritten.
    line_pattern = re.compile(r'^([ \t]*)' + re.escape(ORIGINAL), re.MULTILINE)
    matches = list(line_pattern.finditer(text))
    if len(matches) != 1:
        raise SystemExit(f'build-fuxi-root-auth: {len(matches)} candidate panic lines, expected 1')

    match = matches[0]
    indent = match.group(1)
    window = text[max(0, match.start() - 4000):match.start()]
    if 'FSIOC_KERNEL_ROOTAUTH' not in window:
        raise SystemExit('build-fuxi-root-auth: the panic is not preceded by the ROOTAUTH ioctl; '
                         'refusing to guess')

    if len(indent) < 1:
        raise SystemExit('build-fuxi-root-auth: the panic line has no indentation')

    replacement = REPLACEMENT_HEAD.format(indent=indent)
    text = text[:match.start()] + replacement + text[match.end():]
    source.write_text(text, encoding='utf-8')

    result = source.read_text(encoding='utf-8')
    if 'continuing on the owner policy' not in result or ORIGINAL in result:
        raise SystemExit('build-fuxi-root-auth: the edit did not land')
    print(f'build-fuxi-root-auth: {source} continues past the root seal check '
          f'(indent {len(indent)} columns)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
