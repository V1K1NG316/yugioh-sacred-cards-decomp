#!/usr/bin/env python3
"""Verify baserom.gba against the original ROM."""

import argparse
import hashlib
import shutil
import sys
import os

ORIGINAL = r'D:\Yugioh_DeComp_V2\rom\sacred_cards_usa.gba'
BASEROM = r'D:\Yugioh_DeComp_V2\private\baserom.gba'
SIZE = 16777216
SHA1 = 'd3710031520d9cdae70d870c60b1667285fe5230'
SHA256 = '12d28e0994cbe3a6cc4903fdd3434646c6e912142b73324ffabb2b322a04a411'


def check(label, path):
    if not os.path.exists(path):
        print(f'{label}  MISSING')
        return False
    length = os.path.getsize(path)
    sha1_h = hashlib.sha1()
    sha256_h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha1_h.update(chunk)
            sha256_h.update(chunk)
    s1 = sha1_h.hexdigest().lower()
    s2 = sha256_h.hexdigest().lower()
    ok = (length == SIZE and s1 == SHA1 and s2 == SHA256)
    tag = 'OK' if ok else 'MISMATCH'
    print(f'{label}  size={length}  sha1={s1}  sha256={s2}  {tag}')
    return ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--copy', action='store_true',
                        help='Copy original to baserom.gba if it does not exist')
    args = parser.parse_args()

    if args.copy and not os.path.exists(BASEROM):
        shutil.copyfile(ORIGINAL, BASEROM)
        print(f'Copied {ORIGINAL} -> {BASEROM}')

    r1 = check('ORIGINAL', ORIGINAL)
    r2 = check('BASEROM',  BASEROM)
    sys.exit(0 if (r1 and r2) else 1)


if __name__ == '__main__':
    main()
