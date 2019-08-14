# run-nb

Basically [nbrun](https://github.com/tritemio/nbrun) with email notifications.

## Quickstart

```shell
python3 -m venv pyenv
. pyenv/bin/activate
pip install -r requirements.txt
mv config.ini.example config.ini
# set email in config.ini
python run-nb.py example.ipynb
```
