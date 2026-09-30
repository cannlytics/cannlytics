"""
Audit Git History for Secrets | Cannlytics admin script
Copyright (c) 2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/29/2026
Updated: 9/29/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Lists every distinct credential-shaped string ever added to or
    removed from any commit on any branch (including remote branches),
    masked, with the files it appeared in, the first and last commit
    dates, and whether it is still in the current tree. For a private
    key it also reports the service account and key ID when the same
    file shows them, so you can check whether the key still exists.

    Run from the repository root; nothing is printed unmasked:

        python audit_history_secrets.py
        python audit_history_secrets.py --csv secrets.csv

    Keep this script, and its output, out of the repository.
"""
# Standard imports:
import argparse
import csv
import re
import subprocess
import sys
from collections import defaultdict

KINDS = {
    'Google API key': r'AIza[0-9A-Za-z_\-]{35}',
    'Private key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'Anthropic API key': r'sk-ant-[A-Za-z0-9_\-]{20,}',
    'OpenAI API key': r'sk-proj-[A-Za-z0-9_\-]{20,}',
    'xAI API key': r'xai-[A-Za-z0-9]{20,}',
    'PyPI token': r'pypi-AgE[A-Za-z0-9_\-]{20,}',
}
# The same filter as the manual scan (POSIX ERE, for git's -G).
GIT_FILTER = ('sk-ant-[A-Za-z0-9]|sk-proj-|xai-[A-Za-z0-9]{20}|AIza[0-9A-Za-z_-]{30}'
              '|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|pypi-AgE')
KEY_ID = re.compile(r'"private_key_id"\s*:\s*"([0-9a-f]{8,})"')
CLIENT = re.compile(r'"client_email"\s*:\s*"([^"]+)"')
ACTION = {
    'Google API key': ('Google Cloud console > APIs & Services > Credentials. A Firebase web key is '
                       'public by design: make sure it is restricted (HTTP referrers, API list). '
                       'Any other key: delete or regenerate it.'),
    'Private key': ('IAM & Admin > Service accounts > this account > Keys: if the key ID is still '
                    'listed, delete it. Gone or unknown: nothing more to do.'),
    'Anthropic API key': 'Console > API keys: delete it if it still exists.',
    'OpenAI API key': 'Platform > API keys: delete it if it still exists.',
    'xAI API key': 'Console > API keys: delete it if it still exists.',
    'PyPI token': 'Account settings > API tokens: remove it if it still exists.',
}

def git(*args):
    """Run git; return stdout as text (undecodable bytes replaced)."""
    result = subprocess.run(['git', *args], capture_output=True)
    if result.returncode not in (0, 1):
        sys.exit(result.stderr.decode('utf-8', 'replace').strip() or f'git {args[0]} failed')
    return result.stdout.decode('utf-8', 'replace')

def mask(value):
    return value if len(value) <= 14 else f'{value[:8]}...{value[-4:]}'

def main(argv=None):
    parser = argparse.ArgumentParser(description='Report credentials in Git history, masked.')
    parser.add_argument('--csv', help='also write the report to this CSV file')
    args = parser.parse_args(argv)

    log = git('log', '--all', '-p', '--no-textconv', '--no-ext-diff', '--no-color',
              f'-G{GIT_FILTER}', '--format=@@COMMIT %H %ad', '--date=short')
    found = defaultdict(lambda: {'files': set(), 'dates': set(), 'commits': set(), 'extra': {}})
    context = defaultdict(dict)      # (commit, file) -> private_key_id / client_email
    headers = []                     # (commit, file, date) with a private key header
    commit = date = path = None
    for line in log.splitlines():
        if line.startswith('@@COMMIT '):
            _, commit, date = line.split(' ', 2)
            continue
        if line.startswith('diff --git '):
            path = line.rsplit(' b/', 1)[-1]
            continue
        if not line or line[0] not in '+-' or line.startswith(('+++ ', '--- ')):
            continue
        text = line[1:]
        for pattern, name in ((KEY_ID, 'key_id'), (CLIENT, 'client_email')):
            match = pattern.search(text)
            if match:
                context[(commit, path)][name] = match.group(1)
        for kind, pattern in KINDS.items():
            for value in set(re.findall(pattern, text)):
                if kind == 'Private key':
                    headers.append((commit, path, date))
                    continue
                entry = found[(kind, value)]
                entry['files'].add(path)
                entry['dates'].add(date)
                entry['commits'].add(commit)

    # Private keys are told apart by key ID when the file shows one, else by file.
    for commit, path, date in headers:
        info = context.get((commit, path), {})
        entry = found[('Private key', info.get('key_id') or f'(no key ID) {path}')]
        entry['files'].add(path)
        entry['dates'].add(date)
        entry['commits'].add(commit)
        if info.get('client_email'):
            entry['extra']['account'] = info['client_email']

    tree_keys = set(git('grep', '-l', '-E', 'BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY', 'HEAD').split())
    rows = []
    for (kind, value), entry in sorted(found.items(), key=lambda item: (item[0][0], max(item[1]['dates']))):
        if kind == 'Private key':
            in_tree = any(f'HEAD:{f}' in tree_keys for f in entry['files'])
            shown = value if value.startswith('(no key ID)') else f'key ID {value[:8]}...'
        else:
            in_tree = bool(git('grep', '-l', '-F', '-e', value, 'HEAD').strip())
            shown = mask(value)
        files = sorted(entry['files'])
        rows.append({
            'kind': kind, 'value': shown, 'account': entry['extra'].get('account', ''),
            'first': min(entry['dates']), 'last': max(entry['dates']), 'commits': len(entry['commits']),
            'in_current_tree': 'YES' if in_tree else 'no',
            'files': '; '.join(files[:4]) + (f' (+{len(files) - 4} more)' if len(files) > 4 else ''),
        })

    if not rows:
        print('No credential-shaped strings in any commit on any branch.')
        return 0
    print(f'{len(rows)} distinct credential(s) in history:\n')
    for row in rows:
        print(f"{row['kind']}: {row['value']}" + (f"  ({row['account']})" if row['account'] else ''))
        print(f"   seen {row['first']} to {row['last']} in {row['commits']} commit(s); "
              f"in the current tree: {row['in_current_tree']}")
        print(f"   files: {row['files']}")
    print('\nWhat to check, by kind:')
    for kind in sorted({row['kind'] for row in rows}):
        print(f'   {kind}: {ACTION[kind]}')
    if args.csv:
        with open(args.csv, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f'\nWritten to {args.csv} (masked).')
    return 0

if __name__ == '__main__':
    sys.exit(main())
