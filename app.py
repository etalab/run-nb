import configparser

from pathlib import Path

from flask import Flask, render_template, send_from_directory, abort

from jobs import get_jobs

app = Flask(__name__)
jobs = get_jobs()

SETTINGS = 'config.ini'
config = configparser.ConfigParser()
config.read(SETTINGS)
output_folder = Path(config.get('general', 'output_folder'))
notebooks = [x.parts[-1] for x in output_folder.iterdir() if x.is_dir()]


@app.route('/')
def index():
    return render_template('index.html', notebooks=sorted(notebooks))


@app.route('/notebook/<notebook>')
def notebook(notebook):
    if notebook not in notebooks:
        abort(404)
    path = Path(output_folder) / notebook
    print(path)
    # protect against tree crawling
    try:
        path.resolve()
        path.relative_to(output_folder)
    except ValueError:
        abort(404)
    outputs = sorted([x.parts[-1] for x in path.iterdir() if x.suffix == '.html'], reverse=True)
    return render_template('notebook.html', outputs=outputs, notebook=notebook)


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
