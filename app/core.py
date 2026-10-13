from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
import json
import subprocess
import uuid
import zipfile

TEXT_EXTENSIONS = {'.java', '.kt', '.xml', '.smali', '.json', '.txt', '.properties'}


@dataclass(frozen=True)
class Addition:
    file: str
    line: int
    text: str


def files(root):
    return {p.relative_to(root).as_posix(): p for p in Path(root).rglob('*')
            if p.is_file() and p.suffix.lower() in TEXT_EXTENSIONS}


def read(path):
    return Path(path).read_text(encoding='utf-8', errors='replace')


def additions(old_root, new_root):
    old = files(old_root)
    result = []
    for name, path in sorted(files(new_root).items()):
        before = read(old[name]).splitlines() if name in old else []
        after = read(path).splitlines()
        for kind, _, _, start, end in SequenceMatcher(None, before, after, autojunk=False).get_opcodes():
            if kind in ('insert', 'replace'):
                result.extend(Addition(name, i + 1, after[i]) for i in range(start, end))
    return result


class Project:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.index = self.root / 'versions.json'
        self.versions = json.loads(self.index.read_text('utf-8')) if self.index.exists() else []

    def decompile(self, apk, executable, label):
        apk = Path(apk).resolve()
        if not zipfile.is_zipfile(apk):
            raise ValueError('Fișierul selectat nu este un APK/ZIP valid.')
        with zipfile.ZipFile(apk) as archive:
            if not any(n.startswith('classes') and n.endswith('.dex') for n in archive.namelist()):
                raise ValueError('APK-ul nu conține classes*.dex. Selectează APK-ul de bază, nu un split de resurse.')
        identifier = uuid.uuid4().hex
        output = self.root / identifier
        command = [str(executable), '--show-bad-code', '-d', str(output), str(apk)]
        # Windows requires cmd.exe for JADX's official .bat launcher.
        if str(executable).lower().endswith(('.bat', '.cmd')):
            command = ['cmd.exe', '/d', '/s', '/c', subprocess.list2cmdline(command)]
        completed = subprocess.run(command, capture_output=True, text=True, errors='replace',
                                   creationflags=subprocess.CREATE_NO_WINDOW if __import__('os').name == 'nt' else 0)
        output.mkdir(parents=True, exist_ok=True)
        (output / 'jadx.log').write_text(completed.stdout + completed.stderr, encoding='utf-8')
        if completed.returncode:
            raise RuntimeError(f'JADX a raportat erori. Rezultatele parțiale și jurnalul sunt în {output}.')
        version = {'id': identifier, 'label': label or apk.stem, 'apk': str(apk)}
        updated = self.versions + [version]
        temporary = self.index.with_suffix('.tmp')
        temporary.write_text(json.dumps(updated, ensure_ascii=False, indent=2), encoding='utf-8')
        temporary.replace(self.index)
        self.versions = updated
        return version

    def directory(self, version):
        return self.root / version['id']
