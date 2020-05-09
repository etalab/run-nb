import requests
from pathlib import Path

from config import get_nb_config

config = get_nb_config()


class RemoteNotebookException(Exception):
    pass


# TODO: handle cache
def get(nb_name, nb_url, nb_depends=[]):
    for dep in nb_depends:
        get(dep['name'], dep['url'])
    nb_folder = Path(config['notebook_folder'])
    nb_folder.mkdir(parents=True, exist_ok=True)
    if not nb_url.endswith('.ipynb'):
        raise RemoteNotebookException(f'"{nb_url}" does not end w/ .ipynb')
    r = requests.get(nb_url, allow_redirects=True)
    nb_path = nb_folder / f'{nb_name}.ipynb'
    with nb_path.open('wb') as nfile:
        nfile.write(r.content)
    return nb_path
