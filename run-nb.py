import os
import click
import configparser
import toml

from datetime import datetime
from pathlib import Path

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from lib.nbrun import run_notebook
from mailer import send_email

DB_DSN = os.environ.get('DATABASE_URL', 'sqlite:///jobs.db')
jobstores = {'default': SQLAlchemyJobStore(url=DB_DSN)}
scheduler = BlockingScheduler(jobstores=jobstores)


@click.group()
def cli():
    pass


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


@cli.command()
@click.option('--settings', default='config.ini', help='Config file', type=click.Path(exists=True))
def schedule(settings):
    click.echo('Scheduling jobs...')
    config = configparser.ConfigParser()
    config.read(settings)

    nb_folder = config.get('general', 'notebook_folder')

    if not Path(nb_folder).exists():
        raise click.ClickException(f'Notebook folder "{nb_folder}" does not exist.')

    with open('jobs.toml') as jfile:
        jobs = toml.loads(jfile.read())

    for job_name, job_data in jobs.items():
        nb_path = Path(job_data.get('notebook'))
        if not nb_path.is_absolute():
            nb_path = Path(nb_folder) / nb_path
        if not nb_path.exists():
            click.echo(f'Notebook file "{nb_path}" not found.', error=True)
            continue
        if not job_data.get('cron'):
            click.echo(f'Job "{job_name}" not scheduled', error=True)
            continue
        # this env var can be used by notebooks
        os.environ['WORKING_DIR'] = str(nb_path.parent)
        scheduler.add_job(
            execute,
            args=(job_name, nb_path, config),
            kwargs={
                'mail_to': job_data.get('mail_to'),
                'only_errors': job_data.get('only_errors'),
                'pdf': job_data.get('pdf')
            },
            trigger=CronTrigger.from_crontab(job_data.get('cron')),
            replace_existing=True,
            id=job_name
        )
        click.echo(f'Job "{job_name}" scheduled.')
    scheduler.print_jobs()
    click.echo('Press Ctrl+C to exit')
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        click.echo('Bye')


if __name__ == '__main__':
    cli()
