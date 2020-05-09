from pathlib import Path

from flask import Flask, render_template, send_from_directory, abort

import config

from jobs import get_jobs

app = Flask(__name__)
jobs = get_jobs()

output_folder = Path(config.get_nb_config()['output_folder'])
notebooks = [x.parts[-1] for x in output_folder.iterdir() if x.is_dir()]


@app.route('/')
def index():
    return render_template('index.html', notebooks=sorted(notebooks))


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
    outputs = sorted([x for x in path.iterdir() if x.suffix == '.html'], reverse=True)
    for o in outputs:
        with open(o) as ofile:
            is_error = 'Error occurred during execution' in ofile.read()
        res.append((o.parts[-1], is_error))
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
