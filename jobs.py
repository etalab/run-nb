import os
import toml
import configparser

from datetime import datetime
from pathlib import Path

from lib.nbrun import run_notebook
from mailer import send_email


def get_jobs():
    with open('jobs.toml') as jfile:
        return toml.loads(jfile.read())


class JobConfException(Exception):
    pass


class JobFatalException(Exception):
    pass


def get_job_execution_info(job_name, settings):
    config = configparser.ConfigParser()
    config.read(settings)

    nb_folder = config.get('general', 'notebook_folder')
    if not Path(nb_folder).exists():
        raise JobFatalException(f'Notebook folder "{nb_folder}" does not exist.')

    jobs = get_jobs()

    job_data = jobs.get(job_name)
    if not job_data:
        raise JobConfException(f'Job "{job_name}" not found.')

    nb_path = Path(job_data.get('notebook'))
    if not nb_path.is_absolute():
        nb_path = Path(nb_folder) / nb_path
    if not nb_path.exists():
        raise JobConfException(f'Notebook file "{nb_path}" not found.')
    cron = job_data.get('cron')
    if not cron:
        raise JobConfException(f'No cron found for job "{job_name}"')

    # this env var can be used by notebooks
    os.environ['WORKING_DIR'] = str(nb_path.parent)

    return (job_name, nb_path, config), {
        'mail_to': job_data.get('mail_to'),
        'only_errors': job_data.get('only_errors'),
        'pdf': job_data.get('pdf')
    }, cron


def execute(nb_name, nb_path, config,
            mail_to=None, only_errors=False, pdf=False):
    """Execute a notebook and send an email if asked"""
    output_folder = config.get('general', 'output_folder')
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
                nb_name, out_path, config, pdf,
                email=mail_to, is_error=is_error
            )
