from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, send_from_directory, abort

import config

from jobs import get_jobs

ERR_STR = 'Error occurred during execution'

app = Flask(__name__)
notebooks = get_jobs()

output_folder = Path(config.get_nb_config()['output_folder'])


@app.route('/')
def index():
    data = []
    for (j, j_data) in notebooks.items():
        n_data = {}
        n_data['notebook'] = j
        n_data['cron'] = j_data['cron']
        path = Path(output_folder) / j
        if path.exists():
            runs = sorted([x for x in path.iterdir() if x.suffix == '.html'], reverse=True)
            n_data['nb_runs'] = len(runs)
            with runs[0].open() as nfile:
                n_data['last_status'] = 'error' if ERR_STR in nfile.read() else 'success'
                n_data['_class'] = 'danger' if n_data['last_status'] == 'error' else 'success'
            n_data['last_run'] = datetime.fromtimestamp(runs[0].stat().st_mtime)
        else:
            n_data['nb_runs'] = 0
            n_data['_class'] = 'warning'
        data.append(n_data)
    return render_template('index.html', notebooks=data, dtnow=datetime.now())


@app.route('/notebook/<notebook>')
def notebook(notebook):
    if notebook not in notebooks:
        abort(404)
    path = Path(output_folder) / notebook
    # protect against tree crawling
    try:
        path.resolve()
        path.relative_to(output_folder)
    except ValueError:
        abort(404)
    res = []
    if path.exists():
        outputs = sorted([x for x in path.iterdir() if x.suffix == '.html'], reverse=True)
        for o in outputs:
            with open(o) as ofile:
                is_error = ERR_STR in ofile.read()
            res.append((o.parts[-1], is_error))
    else:
        res = []
    return render_template('notebook.html', outputs=res, notebook=notebook)


@app.route('/notebook/<notebook>/<output>')
def output(notebook, output):
    path = Path(output_folder) / notebook
    if not path.exists():
        abort(404)
    # protect against tree crawling
    file_path = path / Path(output)
    try:
        file_path.resolve()
        file_path.relative_to(output_folder)
    except ValueError:
        abort(404)
    if not file_path.suffix == '.html':
        abort(404)
    return send_from_directory(path, output)
