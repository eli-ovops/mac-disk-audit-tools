"""Delete only the explicitly approved old App parent .git, after fresh proof."""
import hashlib
import json
import os
import plistlib
import shutil
import stat
import subprocess
import time
from pathlib import Path

SOURCE = Path('/Users/USER/Documents/app/.git')
BACKUP = Path('/Volumes/EXTERNAL/内置盘项目转存/App-20261004-待验收/.git')
EVIDENCE = Path('/Users/USER/Documents/磁盘清理审计/父Git精确清理-20261004.回执.json')
REPORT = Path('/Users/USER/Documents/磁盘清理审计/外置磁盘迁移方案.md')
COPY_RECEIPT = Path('/Volumes/EXTERNAL/内置盘项目转存/App-20261004-待验收.验收.json')
EXPECTED_UUID = '75C1D88E-4702-444C-B356-8CC282CBD720'
EXPECTED_HEAD = 'd61ae2d8216b8f4edbd8f7bfa8ebb8ae9fbd1097'
START = time.monotonic()
DEADLINE = START + 600
ENV = {'GIT_OPTIONAL_LOCKS': '0', 'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'LC_ALL': 'C'}
helper = {}
exec(Path('/Users/USER/Documents/磁盘清理审计/App保留性复制-20261004.py').read_text().split('\nrecord = ')[0], helper)
helper['DEADLINE'] = DEADLINE
meta = helper['metadata']
digest = helper['digest']
child_relatives = [
    '.agents/tools/tuist', '.agents/tools/idb', '.agents/tools/XcodeGen',
    '.agents/tools/XcodeGen/.build/checkouts/Yams',
    '.agents/tools/XcodeGen/.build/checkouts/XcodeProj',
    '.agents/tools/XcodeGen/.build/checkouts/ArtifactBundleGen',
    '.agents/tools/XcodeGen/.build/checkouts/Version',
    '.agents/tools/XcodeGen/.build/checkouts/JSONUtilities',
    '.agents/tools/XcodeGen/.build/checkouts/Rainbow',
    '.agents/tools/XcodeGen/.build/checkouts/SwiftCLI',
    '.agents/tools/XcodeGen/.build/checkouts/Spectre',
    '.agents/tools/XcodeGen/.build/checkouts/AEXML',
    '.agents/tools/XcodeGen/.build/checkouts/PathKit',
    '.agents/tools/Maestro', '.agents/tools/ios-simulator-mcp',
    '.agents/tools/XcodeBuildMCP', '.agents/tools/periphery',
    '.agents/tools/SwiftFormat', '.agents/tools/SwiftLint',
    '.agents/skills/blender-agent-studio', '.agents/skills/coa-tools-2',
    '.agents/skills/blender-skills', '.agents/skills/motion-design-source',
    'focumi', '自律宠物-iOS',
]
record = {
    'authorization': 'User explicitly approved permanent deletion of the exact source parent .git after target/cost disclosure in PMO; relayed by existing Owner continuation.',
    'authorization_source_thread': '01a0cbf6-283e-73f1-9e91-55fb02e6518c',
    'routing_version': 'ROUTING-2026-09-30-v3', 'actual_model_effort': 'UNKNOWN',
    'exact_source_target': str(SOURCE), 'retained_backup': str(BACKUP),
    'method': "shutil.rmtree('.git', dir_fd=open exact source parent directory)",
    'source_scope': 'exact parent .git only', 'backup_write_operations': 0,
    'source_code_write_operations': 0, 'child_git_write_operations': 0,
    'other_cache_delete_operations': 0, 'status': 'PREFLIGHT',
}

def check_budget():
    if time.monotonic() > DEADLINE:
        raise TimeoutError('10-minute exact-object verification limit')

def checkpoint():
    EVIDENCE.write_text(json.dumps(record, ensure_ascii=False, indent=2))

def mount():
    value = plistlib.loads(subprocess.check_output(['/usr/sbin/diskutil', 'info', '-plist', '/Volumes/EXTERNAL']))
    assert value['VolumeUUID'] == EXPECTED_UUID and value['MountPoint'] == '/Volumes/EXTERNAL' and value['Writable']
    for p in (SOURCE, BACKUP):
        assert p.is_dir() and not p.is_symlink() and p.resolve() == p
        assert all(not parent.is_symlink() for parent in p.parents)
    return {k: value.get(k) for k in ('VolumeUUID', 'MountPoint', 'Writable', 'FilesystemType')}

def git(root, *args, optional=False):
    result = subprocess.run(['/usr/bin/git', '-C', str(root), *args], env=ENV,
                            capture_output=True, text=True, timeout=20)
    if not optional and result.returncode:
        raise RuntimeError('read-only Git metadata command failed; no retry')
    return result.returncode, result.stdout.strip()

def summary(root):
    code, head = git(root, 'rev-parse', 'HEAD')
    code, location = git(root, 'rev-parse', '--absolute-git-dir')
    code, common = git(root, 'rev-parse', '--git-common-dir')
    code, refs = git(root, 'for-each-ref', '--format=%(refname)%00%(objectname)')
    code, wt = git(root, 'worktree', 'list', '--porcelain')
    paths = [line[9:] for line in wt.splitlines() if line.startswith('worktree ')]
    core_code, core = git(root, 'config', '--local', '--get', 'core.worktree', optional=True)
    return {'HEAD': head, 'absolute_git_dir': location, 'common_dir': common,
            'ref_count': len(refs.splitlines()), 'ref_metadata_sha256': hashlib.sha256(refs.encode()).hexdigest(),
            'worktree_paths': paths, 'core_worktree': core if core_code == 0 else 'unset'}

def scan(root):
    # Only this exact .git. No project traversal or Git-object contents printed.
    values = {'.': meta(root)}
    for base, directories, files in os.walk(root, followlinks=False):
        check_budget()
        for name in directories + files:
            p = Path(base) / name
            rel = str(p.relative_to(root))
            m = meta(p)
            if not (stat.S_ISREG(m['mode']) or stat.S_ISDIR(m['mode']) or stat.S_ISLNK(m['mode'])):
                raise RuntimeError('unsupported entry in exact Git tree')
            values[rel] = m
    return values

def equivalent_metadata(a, b):
    a, b = dict(a), dict(b)
    a.pop('source_identity'); b.pop('source_identity')
    # The prior verified platform provenance difference is explicitly retained.
    for v in (a, b):
        v['xattr'] = {k: h for k, h in v['xattr'].items() if k != 'com.apple.provenance'}
    return a == b

def activity():
    raw = subprocess.run(['/usr/sbin/lsof', '-nP', '-F', 'pfan'], capture_output=True, text=True, timeout=30)
    assert raw.returncode == 0
    ps = subprocess.check_output(['/bin/ps', '-axo', 'pid=,comm='], text=True)
    git_pids = set()
    for line in ps.splitlines():
        values = line.strip().split(None, 1)
        if len(values) == 2 and (Path(values[1]).name == 'git' or Path(values[1]).name.startswith('git-')):
            git_pids.add(values[0])
    pid = fd = access = None
    matches = []
    for line in raw.stdout.splitlines():
        if line.startswith('p'): pid = line[1:]
        elif line.startswith('f'): fd, access = line[1:], None
        elif line.startswith('a'): access = line[1:]
        elif line.startswith('n'):
            value = line[1:]
            if value == str(SOURCE) or value.startswith(str(SOURCE) + '/') or (pid in git_pids and value == str(SOURCE.parent)):
                matches.append({'pid': pid, 'fd': fd, 'access': access,
                                'path_kind': 'exact Git tree' if value.startswith(str(SOURCE)) else 'Git cwd at source parent'})
    return matches

def df():
    raw = subprocess.check_output(['/bin/df', '-k', str(SOURCE.parent)], text=True)
    row = raw.splitlines()[1].split()
    return {'filesystem': row[0], 'available_KiB': int(row[3]), 'mounted_on': row[-1], 'raw': raw}

try:
    assert not EVIDENCE.exists() and shutil.rmtree.avoids_symlink_attacks
    record['mount'] = mount()
    receipt = json.loads(COPY_RECEIPT.read_text())
    assert receipt['byte_hash_pass'] and receipt['hash_verified_files'] == 96337 and receipt['source_stable']
    record['retained_prior_copy_receipt'] = str(COPY_RECEIPT)
    record['prior_manifest'] = receipt['baseline_manifest_sha256']
    source_summary, backup_summary = summary(SOURCE.parent), summary(BACKUP.parent)
    assert source_summary['absolute_git_dir'] == str(SOURCE)
    assert backup_summary['absolute_git_dir'] == str(BACKUP)
    assert source_summary['HEAD'] == backup_summary['HEAD'] == EXPECTED_HEAD
    assert source_summary['ref_metadata_sha256'] == backup_summary['ref_metadata_sha256']
    assert source_summary['common_dir'] == backup_summary['common_dir'] == '.git'
    assert source_summary['worktree_paths'] == [str(SOURCE.parent)]
    assert backup_summary['worktree_paths'] == [str(BACKUP.parent)]
    assert source_summary['core_worktree'] == backup_summary['core_worktree'] == 'unset'
    for root in (SOURCE, BACKUP):
        assert not (root / 'commondir').exists()
        assert not (root / 'objects/info/alternates').exists()
    record['source_Git_summary'] = source_summary
    record['backup_Git_summary'] = backup_summary
    print(json.dumps({'stage': 'fresh exact-parent-Git comparison; other projects not scanned'}), flush=True)
    before, copied = scan(SOURCE), scan(BACKUP)
    assert set(before) == set(copied)
    mismatches = []
    aggregate = hashlib.sha256()
    regular_count = logical_bytes = allocated_bytes = 0
    inodes = set()
    for rel in sorted(before):
        check_budget()
        a, b = before[rel], copied[rel]
        if not equivalent_metadata(a, b):
            mismatches.append({'relative': rel, 'kind': 'metadata except retained provenance'})
        content_hash = None
        if stat.S_ISREG(a['mode']):
            left, right = digest(SOURCE / rel), digest(BACKUP / rel)
            if left != right: mismatches.append({'relative': rel, 'kind': 'sha256'})
            content_hash = left
            regular_count += 1; logical_bytes += a['size']
        identity = tuple(a['source_identity'][:2])
        if identity not in inodes:
            allocated_bytes += (SOURCE / rel).lstat().st_blocks * 512; inodes.add(identity)
        if meta(SOURCE / rel) != a or meta(BACKUP / rel) != b:
            mismatches.append({'relative': rel, 'kind': 'changed during verification'})
        item = dict(a); item.pop('source_identity')
        aggregate.update(json.dumps([rel, item, content_hash], sort_keys=True, separators=(',', ':')).encode() + b'\n')
    record['fresh_exact_tree_verification'] = {
        'entries': len(before), 'regular_files': regular_count, 'logical_bytes': logical_bytes,
        'source_allocated_bytes': allocated_bytes, 'manifest_sha256': aggregate.hexdigest(),
        'mismatches': mismatches, 'scope': str(SOURCE),
    }
    assert not mismatches
    assert scan(SOURCE) == before and scan(BACKUP) == copied
    children = []
    for relative in child_relatives:
        root = SOURCE.parent / relative
        assert (root / '.git').exists()
        code, head = git(root, 'rev-parse', 'HEAD')
        assert len(head) == 40
        children.append({'repository': str(root), 'git_path': str(root / '.git'), 'HEAD': head})
    record['protected_children_before'] = children
    record['activity_before'] = activity()
    assert not record['activity_before']
    assert not any(rel.endswith('.lock') for rel in before)
    assert source_summary == summary(SOURCE.parent) and backup_summary == summary(BACKUP.parent)
    record['df_before'] = df()
    assert record['df_before']['mounted_on'] == '/System/Volumes/Data'
    record['status'] = 'PREDELETE_GATES_PASSED'
    checkpoint()
    print(json.dumps({'stage': 'predelete gates passed', 'files_verified': regular_count,
                      'logical_bytes': logical_bytes, 'df_before_available_KiB': record['df_before']['available_KiB']}), flush=True)
    with REPORT.open('a') as handle:
        handle.write('\n\n## 2026-10-04 父Git精确永久删除：执行前回执\n\n当前用户在PMO展示精确目标、备份和代价后明确授权永久删除 /Users/USER/Documents/app/.git。仅此对象；旧App根会失去父Git入口，源代码、素材、嵌套Git与旧uv保留。外盘完整父Git仅保留，不覆盖、不修改。新鲜限域逐文件SHA256与指定元数据比对、HEAD/ref/配置摘要、非linked Git/无外worktree或alternates、无当前句柄与Git源cwd使用等门槛已通过。小型原始回执 '+str(EVIDENCE)+'；精确脚本 /Users/USER/Documents/磁盘清理审计/父Git精确清理-20261004.py。不可撤销删除不是一键回迁保证；外盘副本是保留性备份，回迁需另按实际状态处理。\n')
    # One final boundary/stability check; descriptor-based rmtree never follows symlinks.
    record['mount_before_delete'] = mount()
    assert scan(SOURCE) == before and not activity()
    parent_fd = os.open(SOURCE.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        current = os.stat('.git', dir_fd=parent_fd, follow_symlinks=False)
        assert stat.S_ISDIR(current.st_mode)
        assert (current.st_dev, current.st_ino, current.st_ctime_ns) == tuple(before['.']['source_identity'])
        record['delete_started'] = True
        checkpoint()
        shutil.rmtree('.git', dir_fd=parent_fd)
    finally:
        os.close(parent_fd)
    record['delete_returned_normally'] = True
    record['source_exact_path_absent'] = not os.path.lexists(SOURCE)
    assert record['source_exact_path_absent']
    assert BACKUP.is_dir() and not BACKUP.is_symlink()
    after_backup = summary(BACKUP.parent)
    assert after_backup == backup_summary
    assert scan(BACKUP) == copied
    record['backup_Git_summary_after'] = after_backup
    record['backup_exact_metadata_unchanged'] = True
    for child in children:
        root = Path(child['repository'])
        assert (root / '.git').exists()
        code, head = git(root, 'rev-parse', 'HEAD')
        assert head == child['HEAD']
    record['protected_child_git_count'] = len(children)
    record['protected_child_heads_unchanged'] = True
    record['df_after'] = df()
    assert record['df_after']['filesystem'] == record['df_before']['filesystem']
    record['available_net_increase_bytes'] = (record['df_after']['available_KiB'] - record['df_before']['available_KiB']) * 1024
    record['background_activity_caveat'] = 'Same-filesystem observed net availability change; background processes may also write/free space.'
    record['status'] = 'EXACT_PARENT_GIT_DELETED_AND_VERIFIED'
except Exception as exc:
    record['status'] = 'STOPPED_BEFORE_DELETE' if not record.get('delete_started') else 'DELETE_OR_POSTCHECK_FAILED'
    record['error_type'] = type(exc).__name__
    record['error_errno'] = getattr(exc, 'errno', None)
    record['source_exact_path_exists_at_stop'] = os.path.lexists(SOURCE)
    record['backup_exact_path_exists_at_stop'] = BACKUP.is_dir()
finally:
    record['elapsed_seconds'] = time.monotonic() - START
    checkpoint()
    with REPORT.open('a') as handle:
        handle.write('\n父Git精确删除最终回执：'+json.dumps({k: record.get(k) for k in ('status','source_exact_path_absent','protected_child_git_count','protected_child_heads_unchanged','backup_exact_metadata_unchanged','available_net_increase_bytes','error_type','elapsed_seconds')}, ensure_ascii=False)+'。原始df及复核元数据保留于回执JSON；后台活动可能影响净变化，候选目录分配量不冒充释放结果。未删除ModuleCache、index、旧uv或任何项目源码/素材。\n')
    print(json.dumps({k: record.get(k) for k in ('status','source_exact_path_absent','protected_child_git_count','protected_child_heads_unchanged','backup_exact_metadata_unchanged','available_net_increase_bytes','error_type','elapsed_seconds')}, ensure_ascii=False), flush=True)
