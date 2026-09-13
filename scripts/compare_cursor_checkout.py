#!/usr/bin/env python3
"""Compare every package source file with a verified Cursor origin/main checkout."""
import argparse
import csv
import difflib
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IGNORED = {'.git', 'node_modules', '__pycache__', '.DS_Store', '.audit'}
NATIVE_INFRA = {'plugins', 'codex', 'cursor', 'scripts', 'tests', '.agents', '.github'}


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def inventory(root, stack=False):
    result = {}
    for path in root.rglob('*'):
        relative = path.relative_to(root)
        if not path.is_file() or any(part in IGNORED for part in relative.parts):
            continue
        if stack and (relative.parts[0] in {'plugins', 'team-kit'}
                      or relative.as_posix().startswith('docs/comparisons/')):
            continue
        result[relative.as_posix()] = path
    return result


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path else ''


def counterpart(package, name):
    if package == 'stack' and name == 'skills/shelly-mode/references/review-triage.md':
        return 'skills/shelly-mode/references/bugbot-triage.md'
    if package == 'stack' and name.startswith('automations/shelly/'):
        return name.replace('automations/shelly/', 'automations/benny/').replace('setup-shelly', 'setup-benny')
    if package == 'team-kit' and name.startswith('rules/'):
        return 'skills/typescript-conventions/SKILL.md'
    return name


def decision(package, name, status):
    if status == 'identical':
        return 'Retained byte-for-byte.'
    if name.startswith('.cursor-plugin/'):
        return 'Excluded editor manifest; registered separate native Claude and Codex manifests.'
    if name.startswith('assets/') or name.startswith('docs/guide/images/'):
        return 'Presentation asset; no agent capability. Native manifests keep their own presentation metadata.'
    if package == 'team-kit':
        if name.startswith('rules/'):
            return 'Adapted both editor rules into typescript-conventions; no alwaysApply editor hook.'
        if name.startswith('agents/'):
            return 'Claude entrypoints plus shared reviewer references; Codex uses native contained subagents.'
        if 'pr-review-canvas' in name:
            return 'Native preview with safe JSON, escaped source text, pagination, full-path keys and correct line numbers.'
        return 'Native companion workflow, scoped writes and merges, current-head checks, available UI/CLI tools and explicit invocation policy.'
    if name.startswith('skills/principle-'):
        return 'Portable principle retained or updated; native invocation and tool wording preserved. All 23 are bundled and routed.'
    if name.startswith('skills/how/'):
        return 'Updated explanation-only workflow and prompt references; removed both retired critic references; retained native read-only roles.'
    if name.startswith('skills/why/'):
        return 'Ported workflow simplification; retained seven evidence categories and native connector discovery instead of Cursor’s four-category restriction.'
    if name.startswith('skills/setup-shelly-stack/'):
        return 'Retained native model/effort discovery and launch checks; removed retired how-critics role. Excluded Task-enum slugs and Cursor custom agent types.'
    if name.startswith('skills/shelly-mode/scripts/orch/'):
        return 'Retained authoritative remote head SHAs and native chain contract; excluded Cursor local-ref frontier and closed-ancestor behavior.'
    if name.startswith('skills/shelly-mode/scripts/watch-pr/'):
        return 'Retained generic native PR watcher; excluded Cursor/Bugbot run classification and pass counters.'
    if name.startswith('automations/'):
        return 'Retained dormant native automation pack. No Cursor scheduler, credential settings, or automation activation imported.'
    if name.startswith('agents/'):
        return 'Retained native Claude agents. Excluded Cursor custom types, model slugs, and background/cloud metadata.'
    if name.startswith('skills/shelly-mode/'):
        return 'Ported portable workflow and prose updates, 23-principle routing and Team Kit references. Retained native forge, verification, scheduling, isolation and authorization.'
    if name.startswith('skills/'):
        return 'Ported portable content changes; retained native skill invocation, configured roles, scoped transcripts and available tool handling.'
    if name.startswith('docs/') or name == 'README.md':
        return 'Native documentation retained; updated principle count, explanation workflow and companion package. Cursor setup instructions excluded.'
    if Path(name).parts[0] in NATIVE_INFRA:
        return 'Native build, runtime override or verification source; preserved and updated for the new shared workflows.'
    return 'Native packaging or shared source; preserve applicable licensing and runtime metadata.'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkout', type=Path)
    args = parser.parse_args()
    source = args.checkout.resolve()
    head = git(source, 'rev-parse', 'HEAD')
    remote = git(source, 'ls-remote', 'origin', 'refs/heads/main').split()[0]
    if head != remote or git(source, 'status', '--porcelain', '--', 'shelly-stack', 'shelly-team-kit'):
        raise SystemExit('Cursor package checkout must be clean and match live origin/main. Fetch and update it first.')
    out = ROOT / 'docs/comparisons'
    out.mkdir(exist_ok=True)
    rows, patch, inventories = [], [], {}
    for package, upstream, native in [('stack', source / 'shelly-stack', ROOT),
                                      ('team-kit', source / 'shelly-team-kit', ROOT / 'team-kit')]:
        sources = inventory(upstream)
        targets = inventory(native, stack=package == 'stack')
        mapped = set()
        for name, path in sorted(sources.items()):
            target_name = counterpart(package, name)
            mapped.add(target_name)
            target = targets.get(target_name)
            status = 'source-only' if target is None else 'identical' if digest(path) == digest(target) else 'adapted'
            rows.append([package, name, target_name if target else '', status, digest(path), digest(target), decision(package, name, status)])
            try:
                patch.extend(difflib.unified_diff(
                    path.read_text().splitlines(True), target.read_text().splitlines(True) if target else [],
                    fromfile=f'cursor/{package}/{name}', tofile=f'native/{package}/{target_name}'))
            except UnicodeDecodeError:
                pass
        for name in sorted(targets.keys() - mapped):
            rows.append([package, '', name, 'native-only', '', digest(targets[name]), decision(package, name, 'native-only')])
        inventories[package] = {'cursor_files': len(sources), 'native_files': len(targets)}
    with (out / 'cursor-file-comparison.csv').open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['package', 'cursor_file', 'native_file', 'status', 'cursor_sha256', 'native_sha256', 'disposition'])
        writer.writerows(rows)
    (out / 'cursor-source-diff.patch').write_text(''.join(patch))
    principles = sorted(p.parent.name for p in (ROOT / 'skills').glob('principle-*/SKILL.md'))
    source_principles = sorted(p.parent.name for p in (source / 'shelly-stack/skills').glob('principle-*/SKILL.md'))
    if principles != source_principles:
        raise SystemExit('Principle inventories differ from the live Cursor checkout.')
    metadata = {'cursor_head': head, 'verified_origin_main': remote, 'native_head': git(ROOT, 'rev-parse', 'HEAD'),
                'native_changes_committed': False, 'packages': inventories, 'comparison_rows': len(rows),
                'principles': principles, 'excluded_inventory': ['.git', 'node_modules', '__pycache__', '.DS_Store', '.audit', 'generated plugins and comparison reports from source inventory']}
    (out / 'cursor-comparison-metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    outputs = {}
    for name in ['shelly-stack', 'shelly-team-kit', 'shelly-stack-cursor']:
        outputs[name] = {n: digest(p) for n, p in sorted(inventory(ROOT / 'plugins' / name).items())}
    (out / 'distribution-inventory.json').write_text(json.dumps(outputs, indent=2) + '\n')
    print(json.dumps(metadata, indent=2))


if __name__ == '__main__':
    main()
