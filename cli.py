import os
import click

from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from jobs import (
    JobConfException, get_jobs, get_job_execution_info,
    JobFatalException, execute, do_truncate,
)

TIMEZONE = os.getenv('TZ', 'Europe/Paris')


@click.group()
def cli():
    pass


def execute_wrapper(nb_name, nb_path, **kwargs):
    click.echo(f'<-- [{datetime.now().isoformat()}] running job {nb_name} ---')
    execute(nb_name, nb_path, **kwargs)
    click.echo(f'--- [{datetime.now().isoformat()}] job {nb_name} done. -->')


@cli.command()
@click.argument('job_name')
def run(job_name):
    try:
        job_args, job_kwargs, _ = get_job_execution_info(job_name)
    except (JobConfException, JobFatalException) as e:
        click.secho(str(e), err=True, fg='red')
        return
    execute_wrapper(*job_args, **job_kwargs)


@cli.command()
@click.argument('job_name')
@click.argument('truncate_value')
def truncate(job_name, truncate_value):
    """Truncate job runs to given value"""
    count = do_truncate(job_name, truncate=truncate_value)
    click.secho(f'Removed {count} files for job {job_name}.', fg='green')


@cli.command()
def schedule():
    """Schedule jobs from config and launch a blocking scheduler or trigger a job immediately"""
    click.echo('Scheduling jobs...')

    jobs = get_jobs()
    scheduler = BlockingScheduler(timezone=timezone(TIMEZONE))

    for job_name in jobs.keys():
        try:
            job_args, job_kwargs, cron = get_job_execution_info(job_name)
        except JobConfException as e:
            click.secho(str(e), err=True, fg='red')
            continue
        except JobFatalException as e:
            click.secho(str(e), err=True, fg='red')
            return

        scheduler.add_job(
            execute_wrapper,
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
