import json
import subprocess
from pathlib import Path
import tempfile
import sys
from datetime import datetime


js_code = """\
#!/usr/bin/osascript -l JavaScript

function run(input, parameters) {
    var safariTabs = [];
    var safari = Application('Safari');

    safari.windows().forEach(function (window) {
        window.tabs().forEach(function (tab) {
            safariTabs.push({ "name": tab.name(), "url": tab.url() });  // NB: we can get here duplicate pinned tabs
        })
    })
    return JSON.stringify(safariTabs);
}
"""


def main():
    fd, path = tempfile.mkstemp()
    path = Path(path)
    path.write_text(js_code)
    path.chmod(0o755)

    try:
        out = subprocess.check_output([path], stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        print(exc.stderr.decode().strip())
        return 1
    finally:
        path.unlink()

    j = json.loads(out.decode())
    x = []

    dte = datetime.now()
    output_path = Path(f'~/.tmp/safari_git/safari_tabs.md').expanduser()
    (repo_path := output_path.parent).mkdir(parents=True, exist_ok=True)
    #print(output_path)

    with output_path.open("wt") as f:
        for e in j:
            if not e in x:
                x.append(e)
                f.write(f' - [{e["name"]}]({e["url"]})\n')

    try:
        out = subprocess.check_output(['git', f'--git-dir={repo_path.joinpath(".git")}', f'--work-tree={repo_path}',
                                       'commit', '-am', f'Safari {dte:%Y.%m.%d %H:%M:%S}'], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        stdout = exc.stdout.decode().strip()
        if 'nothing to commit, working tree clean' in stdout:
            return 0
        print(stdout)
        return 2


if __name__ == "__main__":
    sys.exit(main())
