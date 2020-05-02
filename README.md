# run-nb

Basically [nbrun](https://github.com/tritemio/nbrun) with email reports. Run a notebook from the command line and get a report in your mailbox, shall it succeeds or fails. Every notebook run is saved both as `.ipynb` and `.html` on the local filesystem.

This can be useful when executing automated/periodical tasks from a notebook.

## Quickstart

```shell
python3 -m venv pyenv
. pyenv/bin/activate
pip install -r requirements.txt
mv config.ini.example config.ini
# set email in config.ini
python run-nb.py example.ipynb
```

### PDF attachment

The report can be sent in PDF too, using the `--pdf` option.

```
python run-nb.py --pdf example.ipynb
```

This requires `wkhtmltopdf`, cf useful links:
- https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf
- https://github.com/JazzCore/python-pdfkit/wiki/Using-wkhtmltopdf-without-X-server
