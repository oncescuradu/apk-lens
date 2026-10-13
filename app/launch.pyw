import os
from pathlib import Path
import runpy

root = Path(__file__).resolve().parent
os.environ['JAVA_HOME'] = str(root / 'tools' / 'java')
os.environ['PATH'] = str(root / 'tools' / 'java' / 'bin') + os.pathsep + os.environ.get('PATH', '')
os.chdir(root)
runpy.run_path(str(root / 'app.py'), run_name='__main__')
