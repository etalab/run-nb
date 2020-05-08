import os
import click
import configparser
import toml

from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from lib.nbrun import run_notebook
from mailer import send_email

scheduler = BlockingScheduler()


@click.group()
def cli():
    pass


def execute(nb_name, nb_path, config,
            mail_to=None, only_errors=False, pdf=False):
    """Execute a notebook and send an email if asked"""
    click.echo(f'<-- [{datetime.now().isoformat()}] running job {nb_name} ---')
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
        click.echo(f'--- [{datetime.now().isoformat()}] job {nb_name} done. -->')


class JobConfException(Exception):
    pass


def get_job_execution_info(job_name, settings):
    config = configparser.ConfigParser()
    config.read(settings)

    nb_folder = config.get('general', 'notebook_folder')
    if not Path(nb_folder).exists():
        raise click.ClickException(f'Notebook folder "{nb_folder}" does not exist.')

    with open('jobs.toml') as jfile:
        jobs = toml.loads(jfile.read())

    job_data = jobs.get(job_name)
    if not job_data:
        click.secho(f'Job "{job_name}" not found.', err=True, fg='red')
        raise JobConfException()

    nb_path = Path(job_data.get('notebook'))
    if not nb_path.is_absolute():
        nb_path = Path(nb_folder) / nb_path
    if not nb_path.exists():
        click.secho(f'Notebook file "{nb_path}" not found.', err=True, fg='red')
        raise JobConfException()
    cron = job_data.get('cron')
    if not cron:
        click.secho(f'No cron found for job "{job_name}"', err=True, fg='red')
        raise JobConfException()

    # this env var can be used by notebooks
    os.environ['WORKING_DIR'] = str(nb_path.parent)

    return (job_name, nb_path, config), {
        'mail_to': job_data.get('mail_to'),
        'only_errors': job_data.get('only_errors'),
        'pdf': job_data.get('pdf')
    }, cron


@cli.command()
@click.argument('job_name')
@click.option('--settings', default='config.ini', help='Config file', type=click.Path(exists=True))
def run(job_name, settings):
    try:
        job_args, job_kwargs, _ = get_job_execution_info(job_name, settings)
    except JobConfException:
        return
    execute(*job_args, **job_kwargs)


@cli.command()
@click.option('--settings', default='config.ini', help='Config file', type=click.Path(exists=True))
def schedule(settings):
    """Schedule jobs from config and launch a blocking scheduler or trigger a job immediately"""
    click.echo('Scheduling jobs...')

    with open('jobs.toml') as jfile:
        jobs = toml.loads(jfile.read())

    for job_name in jobs.keys():
        try:
            job_args, job_kwargs, cron = get_job_execution_info(job_name, settings)
        except JobConfException:
            continue
        scheduler.add_job(
            execute,
            args=job_args,
            kwargs=job_kwargs,
            trigger=CronTrigger.from_crontab(cron),
            replace_existing=True,
            id=job_name
        )
        click.secho(f'- cron "{cron}" set for job "{job_name}".', fg='green')

    scheduler.print_jobs()
    click.secho('Scheduler started!', fg='green')
    click.echo('Press Ctrl+C to exit')
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        click.echo('Bye')


if __name__ == '__main__':
    cli()
