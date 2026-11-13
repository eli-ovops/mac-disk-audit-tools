"""Read-only source revalidation; adjust only copied link timestamps."""
from pathlib import Path
import collections
import json
import os
import stat
import time

script = Path('/Users/USER/Documents/磁盘清理审计/App保留性复制-20261004.py')
scope = {}
exec(script.read_text().split('\nrecord = ')[0], scope)  # Helpers only; never repeat copy.
scope['DEADLINE'] = time.monotonic() + 120
begun = time.monotonic()
source, target, evidence = (scope[k] for k in ('SOURCE', 'TARGET', 'EVIDENCE'))
metadata, inventory, digest, manifest = (scope[k] for k in ('metadata', 'inventory', 'digest', 'manifest'))
record = json.loads(evidence.read_text())
scope['mount_check']()
current = inventory(source)
hashes = {}
unstable = []
for relative, m in current.items():
    if stat.S_ISREG(m['mode']):
        hashes[relative] = digest(source / relative)
    if metadata(source / relative) != m:
        unstable.append(relative)
source_manifest = manifest(current, hashes)
assert source_manifest == record['baseline_manifest_sha256'] and not unstable
source_after = inventory(source)
assert current == source_after

repaired = []
for relative, m in current.items():
    if stat.S_ISLNK(m['mode']):
        path = target / relative
        assert path.is_symlink() and os.readlink(path) == m['link_target']
        if path.lstat().st_mtime_ns != m['mtime_ns']:
            os.utime(path, ns=((source / relative).lstat().st_atime_ns, m['mtime_ns']), follow_symlinks=False)
            repaired.append(relative)

after = inventory(target)
differences = []
platform_added = []
platform_changed = []
source_attribute_loss = []
assert set(current) == set(after)
for relative in sorted(current):
    a, b = dict(current[relative]), dict(after[relative])
    a.pop('source_identity'); b.pop('source_identity')
    if a != b:
        fields = [k for k in a if a[k] != b.get(k)]
        differences.append({'relative': relative, 'kind': 'metadata', 'fields': fields})
        source_attrs = {k: v for k, v in a['xattr'].items() if k != 'com.apple.provenance'}
        target_attrs = {k: v for k, v in b['xattr'].items() if k != 'com.apple.provenance'}
        if fields == ['xattr'] and source_attrs == target_attrs:
            (platform_changed if 'com.apple.provenance' in a['xattr'] else platform_added).append(relative)
        else:
            source_attribute_loss.append(relative)

groups = collections.defaultdict(list)
for relative, m in current.items():
    if stat.S_ISREG(m['mode']):
        groups[tuple(m['source_identity'][:2])].append(relative)
hardlink_groups = [members for members in groups.values() if len(members) > 1]
hardlink_differences = [members for members in hardlink_groups
                        if len({tuple(after[p]['source_identity'][:2]) for p in members}) != 1]
for relative in scope['EXCLUSIONS']:
    assert not os.path.lexists(target / relative)
assert not source_attribute_loss

record['initial_verification'] = {
    'status': record['status'], 'metadata_differences': record['differences'],
    'reported_source_changes': record['source_changes'],
    'reported_source_change_reason': 'controller comparison omitted link_target for symlinks; corrected by full source aggregate hash equality',
}
record.update(status='PARTIAL_COPY_CONTENT_VERIFIED_WITH_PLATFORM_METADATA_DIFFS',
              source_stable=True, source_changes=[],
              source_revalidation_manifest_sha256=source_manifest,
              differences=differences, metadata_pass=not differences,
              source_metadata_preserved=not differences,
              source_metadata_except_platform_provenance_preserved=not source_attribute_loss,
              platform_added_provenance_count=len(platform_added),
              platform_changed_provenance_count=len(platform_changed),
              platform_added_provenance_action='retained; system managed attribute not removed or bypassed',
              copied_link_mtime_repairs=sum('mtime_ns' in x.get('fields', []) for x in record['initial_verification']['metadata_differences']),
              link_mtime_repairs_this_supplement=len(repaired), hardlink_groups=len(hardlink_groups),
              hardlink_topology_pass=not hardlink_differences,
              hardlink_split_group_count=len(hardlink_differences),
              hardlink_split_group_samples=hardlink_differences[:10],
              hardlink_split_groups_manifest_sha256=scope['hashlib'].sha256(json.dumps(hardlink_differences, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest(),
              hardlink_action='retain copied regular files; no unlink/relink because no deletion authorized',
              supplement_seconds=time.monotonic() - begun,
              controller_script_sha256=digest(script),
              supplement_script=str(Path(__file__).resolve()))
evidence.write_text(json.dumps(record, ensure_ascii=False, indent=2))
print(json.dumps({k: record[k] for k in ('status', 'copied_regular_files', 'copied_logical_bytes',
    'copied_symlinks', 'hash_verified_files', 'source_stable', 'source_metadata_preserved',
    'platform_added_provenance_count', 'copied_link_mtime_repairs', 'hardlink_groups',
    'hardlink_topology_pass', 'supplement_seconds')}, ensure_ascii=False))
