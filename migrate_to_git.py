"""Migrate file-based Safari tab data to git-based

Create new directory and initialize git repo:

mkdir -p ~/.tmp/safari_git
git init ~/.tmp/safari_git
git --git-dir=~/.tmp/safari_git/.git --work-tree=~/.tmp/safari_git config user.name "Your Name"
git --git-dir=~/.tmp/safari_git/.git --work-tree=~/.tmp/safari_git config user.email "you@domain.com"
git --git-dir=~/.tmp/safari_git/.git --work-tree=~/.tmp/safari_git commit --allow-empty -am "initial commit"
touch ~/.tmp/safari_git/safari_tabs.md
git --git-dir=~/.tmp/safari_git/.git --work-tree=~/.tmp/safari_git add safari_tabs.md

Then run this script and watch it migrate the data from the file-based tab history to the git-based tab history.
"""

from pathlib import Path
from datetime import datetime, timezone
import subprocess
import shutil
from email.utils import formatdate
from time import mktime


if __name__ == "__main__":
    repo_path = Path("~/.tmp/safari_git").expanduser()
    new_path = repo_path.joinpath('safari_tabs.md')

    for path in sorted(Path("~/.tmp/safari").expanduser().glob("*.md")):
        dte = datetime.strptime(path.stem, "%Y%m%d_%H%M%S")
        print(f"Copying {path} into {new_path}")

        shutil.copy(path, new_path)
        try:
            out = subprocess.check_output(['git', f'--git-dir={repo_path.joinpath(".git")}', f'--work-tree={repo_path}',
                                           'commit', f'--date={formatdate(mktime(dte.timetuple()))}',
                                           '-am', f'Safari {dte:%Y.%m.%d %H:%M:%S}'], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            stdout = exc.stdout.decode().strip()
            print(stdout)
