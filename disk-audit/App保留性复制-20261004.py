"""One authorized preserving copy; no source writes, retries, or deletion."""
import ctypes
import hashlib
import json
import os
import plistlib
import shutil
import stat
import subprocess
import time
from pathlib import Path

SOURCE = Path('/Users/USER/Documents/app')
TARGET = Path('/Volumes/EXTERNAL/内置盘项目转存/App-20261004-待验收')
EVIDENCE = TARGET.with_name(TARGET.name + '.验收.json')
EXCLUSIONS = {'自律宠物-iOS/.asc/artifacts': 'local signed archives: profile/privacy scope UNKNOWN; source retained'}
START = time.monotonic()
DEADLINE = START + 1800
lib = ctypes.CDLL('/usr/lib/libSystem.B.dylib', use_errno=True)
lib.acl_get_link_np.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.acl_get_link_np.restype = ctypes.c_void_p
lib.acl_to_text.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ssize_t)]
lib.acl_to_text.restype = ctypes.c_void_p
lib.acl_free.argtypes = [ctypes.c_void_p]
lib.listxattr.argtypes = [ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
lib.listxattr.restype = ctypes.c_ssize_t
lib.getxattr.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_int]
lib.getxattr.restype = ctypes.c_ssize_t
errors, differences, source_changes, progress = [], [], [], {}

def budget():
    if time.monotonic() > DEADLINE:
        raise TimeoutError('30 minute copy/verification budget')

def digest(path):
    budget()
    h = hashlib.sha256()
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as handle:
        while chunk := handle.read(4 * 1024 * 1024):
            h.update(chunk)
            budget()
    return h.hexdigest()

def acl_hash(path):
    acl = lib.acl_get_link_np(os.fsencode(path), 0x100)
    if not acl:
        errno = ctypes.get_errno()
        if errno in (0, 2, 22, 45, 93):
            return None
        raise OSError(errno, 'ACL metadata read')
    try:
        length = ctypes.c_ssize_t()
        text = lib.acl_to_text(acl, ctypes.byref(length))
        if not text:
            raise OSError(ctypes.get_errno(), 'ACL metadata serialization')
        try:
            return hashlib.sha256(ctypes.string_at(text, length.value)).hexdigest()
        finally:
            lib.acl_free(text)
    finally:
        lib.acl_free(acl)

def metadata(path):
    s = path.lstat()
    attrs = {}
    encoded = os.fsencode(path)
    length = lib.listxattr(encoded, None, 0, 1)  # Darwin XATTR_NOFOLLOW
    if length < 0:
        raise OSError(ctypes.get_errno(), 'native xattr names read')
    names = ctypes.create_string_buffer(length)
    if length and lib.listxattr(encoded, names, length, 1) < 0:
        raise OSError(ctypes.get_errno(), 'native xattr names read')
    for name in names.raw.split(b'\0'):
        if not name:
            continue
        count = lib.getxattr(encoded, name, None, 0, 0, 1)
        if count < 0:
            raise OSError(ctypes.get_errno(), 'native xattr size read')
        value = ctypes.create_string_buffer(count)
        if lib.getxattr(encoded, name, value, count, 0, 1) != count:
            raise OSError(ctypes.get_errno(), 'native xattr value read')
        attrs[os.fsdecode(name)] = hashlib.sha256(value.raw).hexdigest()
    result = {'mode': s.st_mode, 'size': s.st_size if not stat.S_ISDIR(s.st_mode) else None,
            'mtime_ns': s.st_mtime_ns, 'uid': s.st_uid, 'gid': s.st_gid,
            'flags': s.st_flags, 'xattr': attrs, 'acl_sha256': acl_hash(path),
            'source_identity': [s.st_dev, s.st_ino, s.st_ctime_ns]}
    if stat.S_ISLNK(s.st_mode):
        result['link_target'] = os.readlink(path)
    return result

def excluded(relative):
    return any(relative == p or relative.startswith(p + '/') for p in EXCLUSIONS)

def inventory(root):
    result = {}
    for base, dirs, files in os.walk(root, followlinks=False):
        budget()
        for name in dirs + files:
            path = Path(base) / name
            rel = str(path.relative_to(root))
            if excluded(rel):
                continue
            result[rel] = metadata(path)
            mode = result[rel]['mode']
            if stat.S_ISLNK(mode):
                result[rel]['link_target'] = os.readlink(path)
            elif not stat.S_ISREG(mode) and not stat.S_ISDIR(mode):
                raise RuntimeError('unsupported file type: ' + rel)
        dirs[:] = [d for d in dirs if not excluded(str((Path(base) / d).relative_to(root)))]
    return result

def manifest(records, hashes):
    h = hashlib.sha256()
    for relative in sorted(records):
        entry = dict(records[relative])
        entry.pop('source_identity', None)
        h.update(json.dumps([relative, entry, hashes.get(relative)], sort_keys=True,
                            ensure_ascii=False, separators=(',', ':')).encode() + b'\n')
    return h.hexdigest()

def mount_check():
    d = plistlib.loads(subprocess.check_output(['/usr/sbin/diskutil', 'info', '-plist', '/Volumes/EXTERNAL']))
    assert d['VolumeUUID'] == '75C1D88E-4702-444C-B356-8CC282CBD720'
    assert d['MountPoint'] == '/Volumes/EXTERNAL' and d['Writable']
    for parent in TARGET.parents:
        assert not parent.is_symlink()
    return {k: d.get(k) for k in ('VolumeUUID', 'MountPoint', 'Writable', 'FilesystemType', 'GlobalPermissionsEnabled', 'Encryption')}

def copy_partition(relative):
    budget()
    if excluded(relative):
        return
    source = SOURCE / relative
    target = TARGET / relative
    m = before[relative]
    assert not os.path.lexists(target)
    if metadata(source) != m:
        source_changes.append(relative)
        return
    if stat.S_ISLNK(m['mode']):
        os.symlink(m['link_target'], target)
        shutil.copystat(source, target, follow_symlinks=False)
        return
    contains_exclusion = any(p.startswith(relative + '/') for p in EXCLUSIONS)
    if contains_exclusion:
        target.mkdir()
        for child in sorted(source.iterdir()):
            copy_partition(str(child.relative_to(SOURCE)))
        shutil.copystat(source, target, follow_symlinks=False)
        return
    # ditto follows argument symlinks, hence the explicit symlink handling above.
    # Traversed symlinks are copied as links by documented native behavior.
    mount_check()
    process = subprocess.Popen(['/usr/bin/ditto', '--rsrc', '--extattr', '--acl', '-X', str(source), str(target)],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               env=dict(os.environ, DITTOABORT='1'))
    try:
        out, err = process.communicate(timeout=max(1, DEADLINE - time.monotonic()))
    except subprocess.TimeoutExpired:
        process.terminate()  # Only this controller's own newly created ditto PID.
        process.wait(timeout=10)
        raise TimeoutError('own ditto exceeded total budget')
    if process.returncode:
        # Do not expose file contents or arbitrary command output.
        errors.append({'relative': relative, 'exit': process.returncode,
                       'stderr_sha256': hashlib.sha256(err).hexdigest(), 'stderr_bytes': len(err)})
        raise RuntimeError('native copy failed; no retry')

record = {'source': str(SOURCE), 'target': str(TARGET), 'exclusions': EXCLUSIONS,
          'budget_seconds': 1800, 'source_write_operations': 0,
          'deletion_operations': 0, 'git_repair_operations': 0,
          'status': 'IN_PROGRESS', 'routing_version': 'ROUTING-2026-09-30-v3',
          'actual_model_effort': 'UNKNOWN'}
try:
    assert SOURCE.is_dir() and not SOURCE.is_symlink()
    assert not os.path.lexists(TARGET) and not os.path.lexists(EVIDENCE)
    record['mount'] = mount_check()
    record['df_before'] = subprocess.check_output(['/bin/df', '-k', str(SOURCE), '/Volumes/EXTERNAL'], text=True)
    print(json.dumps({'stage': 'source_metadata_and_hash_baseline'}, ensure_ascii=False), flush=True)
    before = inventory(SOURCE)
    logical = sum(m['size'] for m in before.values() if stat.S_ISREG(m['mode']))
    assert shutil.disk_usage('/Volumes/EXTERNAL').free > logical + 1024**3
    hashes = {}
    for relative, m in before.items():
        if stat.S_ISREG(m['mode']):
            hashes[relative] = digest(SOURCE / relative)
            if metadata(SOURCE / relative) != m:
                source_changes.append(relative)
        if len(hashes) and len(hashes) % 20000 == 0 and progress.get('baseline') != len(hashes):
            progress['baseline'] = len(hashes)
            print(json.dumps({'stage': 'baseline', 'hashed_files': len(hashes)}), flush=True)
    if source_changes:
        # Add a local exclusion for each changed source file; no overwrite synchronization.
        for path in source_changes:
            EXCLUSIONS[path] = 'source changed while baseline hashing'
        before = {p: m for p, m in before.items() if not excluded(p)}
        hashes = {p: h for p, h in hashes.items() if p in before}
    record['baseline_manifest_sha256'] = manifest(before, hashes)
    record['included_logical_bytes'] = logical
    print(json.dumps({'stage': 'native_copy', 'included_regular_files': len(hashes), 'logical_bytes': logical}), flush=True)
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.mkdir()
    for child in sorted(SOURCE.iterdir()):
        copy_partition(str(child.relative_to(SOURCE)))
    shutil.copystat(SOURCE, TARGET, follow_symlinks=False)
    print(json.dumps({'stage': 'destination_independent_hash_verification'}), flush=True)
    after = inventory(TARGET)
    destination_hashes = {}
    for relative in sorted(before):
        if relative not in after:
            differences.append({'relative': relative, 'kind': 'missing'})
            continue
        expected, actual = dict(before[relative]), dict(after[relative])
        expected.pop('source_identity'); actual.pop('source_identity')
        if expected != actual:
            differences.append({'relative': relative, 'kind': 'metadata',
                                'fields': [k for k in expected if expected[k] != actual.get(k)]})
        if stat.S_ISREG(before[relative]['mode']):
            destination_hashes[relative] = digest(TARGET / relative)
            if destination_hashes[relative] != hashes[relative]:
                differences.append({'relative': relative, 'kind': 'sha256'})
        if metadata(SOURCE / relative) != before[relative]:
            source_changes.append(relative)
        if len(destination_hashes) and len(destination_hashes) % 20000 == 0 and progress.get('verify') != len(destination_hashes):
            progress['verify'] = len(destination_hashes)
            print(json.dumps({'stage': 'verify', 'hashed_files': len(destination_hashes)}), flush=True)
    extra = sorted(set(after) - set(before))
    differences.extend({'relative': p, 'kind': 'unexpected_destination'} for p in extra)
    current = inventory(SOURCE)
    source_changes.extend(p for p in set(current) ^ set(before) if not excluded(p))
    record.update(copied_regular_files=len(destination_hashes), copied_logical_bytes=sum(after[p]['size'] for p in destination_hashes),
                  copied_symlinks=sum(stat.S_ISLNK(m['mode']) for m in after.values()),
                  copied_directories=sum(stat.S_ISDIR(m['mode']) for m in after.values()),
                  baseline_entries=len(before), destination_entries=len(after),
                  destination_manifest_sha256=manifest(after, destination_hashes),
                  differences=differences, source_changes=sorted(set(source_changes)),
                  hash_verified_files=sum(destination_hashes[p] == hashes.get(p) for p in destination_hashes),
                  byte_hash_pass=not any(x['kind'] in ('missing', 'sha256', 'unexpected_destination') for x in differences),
                  metadata_pass=not differences, source_stable=not source_changes,
                  status='PARTIAL_COPY_VERIFIED' if not differences and not source_changes else 'PARTIAL_COPY_WITH_GAPS')
except Exception as e:
    record.update(status='STOPPED_WITH_GAPS', error_type=type(e).__name__,
                  errors=errors, source_changes=sorted(set(source_changes)), differences=differences)
finally:
    record['elapsed_seconds'] = time.monotonic() - START
    record['functional_migration'] = 'NOT_TESTED'
    record['source_deletion_authorized'] = False
    if TARGET.exists():
        record['df_after'] = subprocess.check_output(['/bin/df', '-k', str(SOURCE), '/Volumes/EXTERNAL'], text=True)
        allocated = 0
        seen = set()
        for base, dirs, files in os.walk(TARGET, followlinks=False):
            for p in [Path(base)] + [Path(base) / n for n in dirs + files]:
                s = p.lstat(); identity = (s.st_dev, s.st_ino)
                if identity not in seen:
                    allocated += s.st_blocks * 512; seen.add(identity)
        record['destination_allocated_bytes'] = allocated
    # Evidence stays beside, never mixed into the source-equivalent copy tree.
    if EVIDENCE.parent.exists() and not EVIDENCE.exists():
        with EVIDENCE.open('x') as handle:
            json.dump(record, handle, ensure_ascii=False, indent=2)
    print(json.dumps({k: record.get(k) for k in ('status', 'copied_regular_files', 'copied_logical_bytes',
                'copied_symlinks', 'hash_verified_files', 'metadata_pass', 'source_stable', 'elapsed_seconds', 'error_type')}, ensure_ascii=False), flush=True)
