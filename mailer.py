import emails

import config


def send_email(notebook, out_path, pdf, email=None, is_error=False):
    mail_config = config.get_mail_config()
    email = email or mail_config['recipient']
    message = 'Notebook output is attached.'
    subject = '%s for notebook %s' % ('ERROR' if is_error else 'SUCCESS', notebook)
    message = emails.html(html='<p>%s</p>' % message,
                          subject=subject,
                          mail_from=email)
    filename = '%s.html' % out_path
    message.attach(data=open(filename, 'rb'), filename='%s.html' % out_path.name)
    if pdf and not is_error:
        filename = '%s.pdf' % out_path
        message.attach(data=open(filename, 'rb'), filename='%s.pdf' % out_path.name)
    smtp = {'host': mail_config['smtp_host'], 'port': 465, 'ssl': True,
            'user': mail_config['smtp_user'],
            'password': mail_config['smtp_password']}
    message.send(to=email, smtp=smtp)
