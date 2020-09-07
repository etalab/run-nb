import os


class ConfigException(Exception):
    pass


def get_var(var, default_value=None):
    var = f'NB_{var.upper()}'
    value = os.getenv(var, default_value)
    if not value:
        raise ConfigException(f'Env var "{var}" not found')
    return value


def get_mail_config():
    keys = ['recipient', 'smtp_user', 'smtp_password', 'smtp_host']
    return {k: get_var(f'mail_{k}') for k in keys}


def get_nb_config():
    return {
        'output_folder': get_var('output_folder', 'output/'),
        'notebook_folder': get_var('notebook_folder', 'notebooks/'),
    }
