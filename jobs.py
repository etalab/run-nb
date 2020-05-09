import toml

import config

from datetime import datetime
from pathlib import Path

from lib.nbrun import run_notebook
from mailer import send_email
from remote_notebook import get as get_remote_nb


def get_jobs():
    with open('jobs.toml') as jfile:
        return toml.loads(jfile.read())


class JobConfException(Exception):
    pass


class JobFatalException(Exception):
    pass


def get_job_execution_info(job_name, settings):
    jobs = get_jobs()
    job_data = jobs.get(job_name)
    if not job_data:
        raise JobConfException(f'Job "{job_name}" not found.')

    try:
        nb_path = get_remote_nb(job_name, job_data['notebook'])
    except Exception as e:
        raise JobConfException(f'Failed to dowload "{nb_path}": {e}')

    cron = job_data.get('cron')
    if not cron:
        raise JobConfException(f'No cron found for job "{job_name}"')

    mail_config = config.get_mail_config()
    # mail_to can be configured per notebook via env var
    mail_to = config.get_var(f'mail_for_{job_name}', mail_config['recipient'])
    return (job_name, nb_path), {
        'mail_to': mail_to,
        'only_errors': job_data.get('only_errors'),
        'pdf': job_data.get('pdf')
    }, cron


def execute(nb_name, nb_path,
            mail_to=None, only_errors=False, pdf=False):
    """Execute a notebook and send an email if asked"""
    output_folder = config.get_nb_config()['output_folder']
    suffix = datetime.now().strftime('%Y%m%d-%H%M%S')
    out_filename = '%s_%s' % (nb_name, suffix)
    out_path = Path(output_folder) / nb_name
    out_path.mkdir(parents=True, exist_ok=True)
    out_path = out_path / out_filename

    is_error = False
    try:
        out_html = '%s.html' % out_path
        run_notebook(str(nb_path), save_html=True, suffix=suffix,
                     out_path_ipynb='%s.ipynb' % out_path,
                     out_path_html=out_html)
        if pdf:
            import pdfkit
            pdfkit.from_file(out_html, '%s.pdf' % out_path)
    except Exception as e: # noqa
        print(e)
        is_error = True
    finally:
        if is_error or not only_errors:
            send_email(
                nb_name, out_path, pdf,
                email=mail_to, is_error=is_error
            )
