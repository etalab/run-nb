import time
import requests
from pathlib import Path

import config

nb_config = config.get_nb_config()
# in seconds
CACHE_MAX_AGE = int(config.get_var('cache_max_age', 10 * 60))


class RemoteNotebookException(Exception):
    pass


def get(nb_name, nb_url, nb_depends=[]):
    for dep in nb_depends:
        get(dep['name'], dep['url'])

    nb_folder = Path(nb_config['notebook_folder'])
    nb_folder.mkdir(parents=True, exist_ok=True)
    if not nb_url.endswith('.ipynb'):
        raise RemoteNotebookException(f'"{nb_url}" does not end w/ .ipynb')
    nb_path = nb_folder / f'{nb_name}.ipynb'

    if nb_path.exists():
        mtime = nb_path.stat().st_mtime
        if time.time() - mtime <= CACHE_MAX_AGE:
            print(f'Found cached notebook "{nb_name}".')
            return nb_path

    r = requests.get(nb_url, allow_redirects=True)
    with nb_path.open('wb') as nfile:
        nfile.write(r.content)
    return nb_path
