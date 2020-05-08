import emails


def send_email(notebook, out_path, config, pdf, email=None, is_error=False):
    if 'email' not in config.sections() or not config.get('email', 'recipient'):
        print('Not sending email, config is not set')
        return
    email = email or config.get('email', 'recipient')
    message = 'Notebook output is attached.'
    subject = '%s for notebook %s' % ('ERROR' if is_error else 'SUCCESS', notebook)
    message = emails.html(html='<p>%s</p>' % message,
                          subject=subject,
                          mail_from=email)
    filename = '%s.html' % out_path
    message.attach(data=open(filename, 'rb'), filename='%s.html' % out_path.name)
    if pdf:
        filename = '%s.pdf' % out_path
        message.attach(data=open(filename, 'rb'), filename='%s.pdf' % out_path.name)
    smtp = {'host': 'smtp.mailjet.com', 'port': 465, 'ssl': True,
            'user': config.get('email', 'smtp_user'),
            'password': config.get('email', 'smtp_password')}
    message.send(to=email, smtp=smtp)
