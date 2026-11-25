"""Build a version-locked local copy. Never writes to WindowsApps."""
import argparse
import hashlib
from pathlib import Path
import shutil
import struct

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = '68cc48434e2768750836d439c7adbcb9375f26a5d5a39ccb3c855cea7bd405d6'
BASELINE_SHA256 = '7b94413ec5103057995afe97530e7b9673b0adba3e2a1d6e087b86dea1636219'
PATCHED_SHA256 = '39956da883bf02111929d0fb68176537ecb2a4cc30c1a900a56037e062cbb97a'
SOURCE_IDENTITY = 'Name="SoundcloudLtd.SoundCloud-MusicAudio"'


def validate_bundle(data):
    if len(data) != 2955088:
        raise ValueError('Unsupported bundle length: expected SoundCloud 2.12.4.0 x64.')
    if struct.unpack_from('<QI', data)[0:2] != (0x1F1903C103BC1FC6, 96):
        raise ValueError('Expected Hermes HBC96.')
    if hashlib.sha1(data[:-20]).digest() != data[-20:]:
        raise ValueError('Invalid Hermes footer checksum.')
    if hashlib.sha256(data).hexdigest() != SOURCE_SHA256:
        raise ValueError('Unsupported bundle SHA-256; refusing to patch another build.')


def patch_bundle(data, baseline=False):
    if not __debug__:
        raise RuntimeError('Do not run with python -O or PYTHONOPTIMIZE.')
    validate_bundle(data)
    b = bytearray(data)
    offset = 796436 + 7097  # Shared SizeUtil object literal.
    if b[offset:offset+9] != bytes.fromhex('72 ac 03 00 00 1c 02 00 00'):
        raise ValueError('Unexpected SizeUtil literal.')
    b[offset+1:offset+9] = struct.pack('<ii', 1175, 675)
    b[-20:] = hashlib.sha1(b[:-20]).digest()
    if not baseline:
        from patch_player import patch_player
        patch_player(b)
    b[-20:] = hashlib.sha1(b[:-20]).digest()
    expected = BASELINE_SHA256 if baseline else PATCHED_SHA256
    if hashlib.sha256(b).hexdigest() != expected:
        raise ValueError('Output differs from the validated patch; nothing was written.')
    return bytes(b)


def prepare(baseline=False):
    src, dst = ROOT / 'original', ROOT / 'compact-80'
    for path in (src, dst):
        if path.is_symlink() or path.is_junction() or path.resolve().parent != ROOT.resolve():
            raise ValueError('Source/output must be ordinary directories inside this project.')
    manifest = (src / 'AppxManifest.xml').read_text(encoding='utf-8')
    if SOURCE_IDENTITY not in manifest or 'Version="2.12.4.0"' not in manifest:
        raise ValueError('Unexpected source package manifest.')
    output = patch_bundle((src / 'Bundle/index.windows.bundle').read_bytes(), baseline)
    manifest = manifest.replace(SOURCE_IDENTITY, 'Name="SoundClaude.Compact80"', 1)
    manifest = manifest.replace('SoundCloud - Music &amp; Audio', 'SoundCloud Compact 80 (local)')
    shutil.copytree(src, dst, dirs_exist_ok=True)
    (dst / 'Bundle/index.windows.bundle').write_bytes(output)
    (dst / 'AppxManifest.xml').write_text(manifest, encoding='utf-8')
    for name in ('AppxSignature.p7x', 'AppxBlockMap.xml'):
        (dst / name).unlink(missing_ok=True)
    print('Prepared:', dst)
    print('Mode:', 'scale only' if baseline else 'compact UI + player patches')
    print('SHA256:', hashlib.sha256(output).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', action='store_true', help='Restore scale-only 80% UI in the same copy')
    args = parser.parse_args()
    prepare(args.baseline)


if __name__ == '__main__':
    main()
