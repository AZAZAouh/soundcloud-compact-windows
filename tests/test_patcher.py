"""Fail-closed checks and optional local-package reproducibility checks."""
import hashlib
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from prepare_compact import patch_bundle, validate_bundle, BASELINE_SHA256, PATCHED_SHA256


class GuardTests(unittest.TestCase):
    def test_truncated_input_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'length'):
            patch_bundle(b'not a package')

    def test_wrong_bytecode_version_is_rejected(self):
        data = bytearray(2955088)
        struct.pack_into('<QI', data, 0, 0x1F1903C103BC1FC6, 99)
        with self.assertRaisesRegex(ValueError, 'HBC96'):
            validate_bundle(data)

    def test_broken_footer_is_rejected(self):
        data = bytearray(2955088)
        struct.pack_into('<QI', data, 0, 0x1F1903C103BC1FC6, 96)
        with self.assertRaisesRegex(ValueError, 'checksum'):
            validate_bundle(data)

    def test_unknown_valid_container_is_rejected(self):
        data = bytearray(2955088)
        struct.pack_into('<QI', data, 0, 0x1F1903C103BC1FC6, 96)
        data[-20:] = hashlib.sha1(data[:-20]).digest()
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            validate_bundle(data)

    @unittest.skipUnless((ROOT / 'original/Bundle/index.windows.bundle').exists(), 'Store bundle is not distributed')
    def test_local_output_matches_verified_builds(self):
        source = (ROOT / 'original/Bundle/index.windows.bundle').read_bytes()
        before = hashlib.sha256(source).hexdigest()
        for baseline, expected in ((True, BASELINE_SHA256), (False, PATCHED_SHA256)):
            output = patch_bundle(source, baseline)
            self.assertEqual(hashlib.sha256(output).hexdigest(), expected)
            self.assertEqual(struct.unpack_from('<I', output, 32)[0], len(output))
            self.assertEqual(hashlib.sha1(output[:-20]).digest(), output[-20:])
        self.assertEqual(hashlib.sha256(source).hexdigest(), before)


if __name__ == '__main__':
    unittest.main()
