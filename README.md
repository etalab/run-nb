# run-nb

Basically [nbrun](https://github.com/tritemio/nbrun) with email reports. Run a notebook from the command line and get a report in your mailbox, shall it succeeds or fails. Every notebook run is saved both as `.ipynb` and `.html` on the local filesystem (and optionally `.pdf`).

This can be useful when executing automated/periodical tasks from a notebook.

There's also a web interface available to display the reports of the notebook runs.

A scheduler is included, you don't need to rely on cron.

## Usage

### Installation

```shell
python3 -m venv pyenv
. pyenv/bin/activate
pip install -r requirements.txt
```

### Environment variables

The following env vars have to be defined for the report to be sent by email:

- `NB_MAIL_RECIPIENT`: who receives the emails
- `NB_MAIL_SMTP_HOST`: SMTP host
- `NB_MAIL_SMTP_USER`: SMTP user
- `NB_MAIL_SMTP_PASSWORD`: SMTP password

### Jobs definition

Jobs (notebook runs) are configured in `jobs.toml`. The jobs will be scheduled or triggered according to the options defined in this file. A job is defined like this:

```toml
[my-job]
# when should the job run (crontab format)
cron = "0 8 * * *"
# where the notebook lives (any http link is fine)
notebook = "https://github.com/etalab/notebooks/raw/schedule/moderation/moderation.ipynb"
# if the notebook depends on other notebooks
# `name` will be used as the name of the notebook on the local copy
depends_on = [
    { name = "moderation_fn", url = "https://github.com/etalab/notebooks/raw/schedule/moderation/moderation_fn.ipynb" }
]
# send email only on errors (or not)
only_errors = true
# attach a PDF version of the report in the email
pdf = true
```

### Run a notebook from the CLI

This will run a job immediately:

```
python cli.py run my-job
```

### Schedule notebook runs

This will launch a (blocking) scheduler that will execute jobs as per the `cron` attribute in config.

```
python cli.py schedule
```

### Run the web interface

```
FLASK_APP=app FLASK_DEBUG=1 flask run
```

## Deployment

### dokku

`Dockerfile` based deployment of both the web interface and the scheduler on `dokku` is included.

On dokku server:

```
dokku apps:create run-nb
```

You need to set the env vars described above via `dokku config:set`.

Deploy a first version:

```
git remote add dokku@{host}:run-nb
git push dokku master
```

Then scale the `scheduler` to one to start scheduling jobs, on the dokku server:

```
dokku ps:scale run-nb scheduler=1
```

### wkhtmltopdf

PDF attachment requires `wkhtmltopdf`, cf useful links:
- https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf
- https://github.com/JazzCore/python-pdfkit/wiki/Using-wkhtmltopdf-without-X-server

The included `Dockerfile` has `wkhtmltopdf` installed.
