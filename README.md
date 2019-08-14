# run-nb

Basically [nbrun](https://github.com/tritemio/nbrun) with email reports. Run a notebook from the command line and get a report in your mailbox, shall it succeeds or fails.

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
