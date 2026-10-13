import tempfile
import unittest
from pathlib import Path
from core import additions, Project
from unittest.mock import patch
import subprocess
import zipfile


class ComparisonTests(unittest.TestCase):
    def test_insert_replace_delete_and_new_file(self):
        with tempfile.TemporaryDirectory() as temp:
            old, new = Path(temp)/'old', Path(temp)/'new'
            old.mkdir()
            new.mkdir()
            (old/'A.java').write_text('same\nremoved\nold\n')
            (new/'A.java').write_text('same\nnew\nadded\n')
            (new/'B.java').write_text('class B {}\n')
            (old/'Deleted.java').write_text('gone\n')
            result = additions(old, new)
            self.assertEqual([(r.file, r.line, r.text) for r in result], [('A.java', 2, 'new'), ('A.java', 3, 'added'), ('B.java', 1, 'class B {}')])

    def test_unchanged_is_empty(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'A.java').write_text('same\n')
            self.assertEqual(additions(root, root), [])

    def test_invalid_apk_does_not_register_version(self):
        with tempfile.TemporaryDirectory() as temp:
            apk = Path(temp)/'bad.apk'
            apk.write_text('invalid')
            project = Project(Path(temp)/'project')
            with self.assertRaises(ValueError):
                project.decompile(apk, 'missing-jadx', 'bad')
            self.assertEqual(project.versions, [])

    def test_import_persists_and_failed_import_keeps_log(self):
        with tempfile.TemporaryDirectory() as temp:
            apk = Path(temp)/'application.apk'
            with zipfile.ZipFile(apk, 'w') as archive:
                archive.writestr('classes.dex', b'fixture')
            project = Project(Path(temp)/'project')
            with patch('core.subprocess.run', return_value=subprocess.CompletedProcess([], 0, 'done', '')) as run:
                version = project.decompile(apk, 'jadx', 'v1')
                self.assertIn('--show-bad-code', run.call_args.args[0])
            self.assertEqual(Project(project.root).versions, [version])
            with patch('core.subprocess.run', return_value=subprocess.CompletedProcess([], 1, 'partial', 'error')):
                with self.assertRaises(RuntimeError):
                    project.decompile(apk, 'jadx', 'v2')
            self.assertEqual(Project(project.root).versions, [version])
            logs = list(project.root.glob('*/jadx.log'))
            self.assertEqual(len(logs), 2)
            self.assertTrue(any('error' in p.read_text() for p in logs))


if __name__ == '__main__':
    unittest.main()
