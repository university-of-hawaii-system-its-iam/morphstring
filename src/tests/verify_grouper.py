"""Optional integration regression against Grouper; requires a JDK and jar."""

import base64
import argparse
import os
import pathlib
import random
import subprocess
import tempfile

import morph

parser = argparse.ArgumentParser(description="Compare Python morphString with a real Grouper client jar; all inputs are test-only.")
parser.add_argument("jar", type=pathlib.Path, help="path to grouperClient-6.4.1.jar")
args = parser.parse_args()
jar = args.jar.resolve(strict=True)
here = pathlib.Path(__file__).resolve().parent
cases = [('je49jwna2jDNcb3', 'letmein7')]
cases += [('k' * n, 'password') for n in (1, 7, 8, 14, 15, 16, 17, 23, 24, 30, 31, 32, 33, 48)]
cases += [('je49jwna2jDNcb3', 'p' * n) for n in (0, 1, 15, 16, 17, 31, 32, 33)]
cases += [('  je49jwna2jDNcb3  ', '\t  password \t'),
          ('je49jwna2jDNcb3', '\x00\x1f password \x1f\x00'),
          ('je49jwna2jDNcb3', '\u00a0password\u00a0'),
          ('je49jwna2jDNcb3', 'pāsswörd🔑/秘密'),
          ('je49jwna2jDNcb3', '  \t'),
          ('é' * 8, 'unicode key valid 24 bytes'),
          ('é' * 16, 'unicode key invalid byte length'),
          ('a' * 30 + '🔑', 'UTF-16 key length'),
          ('a' * 31 + '🔑', 'split surrogate at truncation'),
          ('a' * 32 + '🔑', 'truncated supplementary character')]
rng = random.Random(641)
for _ in range(30):
    key = ''.join(rng.choices('abcdefABCDEF0123456789', k=rng.randrange(1, 65)))
    value = ''.join(rng.choices('abcXYZ 0123/é🔑', k=rng.randrange(0, 100)))
    cases.append((key, value))

vectors = []
with tempfile.TemporaryDirectory(prefix='morph-reference-') as work:
    subprocess.run(['javac', '-encoding', 'UTF-8', '-cp', str(jar), '-d', work,
                    str(here / 'MorphReference.java')], check=True)
    for key, raw in cases:
        data = '\n'.join(base64.b64encode(s.encode()).decode() for s in (key, raw)) + '\n'
        ref = subprocess.run(['java', '-Dfile.encoding=UTF-8', '-cp',
                              os.pathsep.join([work, str(jar)]),
                              'MorphReference'], input=data, text=True, capture_output=True, cwd=work)
        if ref.returncode:
            try:
                morph.encrypt(raw, key)
            except ValueError:
                assert 'Invalid AES key length' in ref.stderr, ref.stderr
                continue
            raise AssertionError((key, raw, ref.stderr))
        lines = dict(line.split('=', 1) for line in ref.stdout.splitlines() if line.startswith(('CIPHER=', 'PLAIN=')))
        expected = lines['CIPHER']
        assert morph.encrypt(raw, key) == expected, (key, raw, expected)
        clear = base64.b64decode(lines['PLAIN']).decode()
        assert morph.decrypt(expected, key) == clear == morph.java_trim(raw)
        vectors.append({'key': key, 'raw': raw, 'encrypted': expected})

print(f'Matched Java for {len(vectors)} encryption/decryption cases; rejected {len(cases) - len(vectors)} invalid keys consistently.')
