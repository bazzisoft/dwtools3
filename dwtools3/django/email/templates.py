import re
from django.conf import settings
from django.template import loader, Template
from django.template.context import Context
from .settings import EmailSettings
from . import messages


CONDENSE_WHITESPACE_RE = re.compile(r'\s+')
REMOVE_INDENTS_RE = re.compile(r'\n +')
LIMIT_NEWLINES_RE = re.compile(r'\n *\n *[\n ]+')


def send_email(user_or_to,
               subject=None, body=None,
               template_prefix=None, vars=None,
               cc=None, bcc=None, frm=None,
               attachments=None, headers=None,
               as_html=True):
    """
    Supports sending a HTML email rendered from templates
    from ``settings.DEFAULT_FROM_EMAIL`` to ``user_or_to``.

    ``user_or_to`` is either a User object, or single/multiple
    recipients as accepted by HTMLEmail.

    If ``subject`` and ``body`` are provided, these are used as the
    email content. They are rendered as Django templates.

    ``template_prefix`` is the path prefix of templates to use for subject
    and body. ``.subject.txt`` and ``.body.html`` are appended to the prefix.

    ``vars`` is an optional dict of key-value pairs that can be injected
    into the email subject and body.

    ``cc``, ``bcc`` and ``frm`` are passed through as extra recipients/sender
    to HTMLEmail.

    ``attachments`` is a list of 3-tuples (filename, content, mimetype).

    ``headers`` is a dict of additional mail headers to set.

    ``as_html`` indicates whether to send a HTML or plain text email.
    """
    vars = vars or {}

    if EmailSettings.EMAIL_EXTRA_TEMPLATE_CONTEXT:
        if callable(EmailSettings.EMAIL_EXTRA_TEMPLATE_CONTEXT):
            vars.update(EmailSettings.EMAIL_EXTRA_TEMPLATE_CONTEXT())
        else:
            vars.update(EmailSettings.EMAIL_EXTRA_TEMPLATE_CONTEXT)

    if hasattr(user_or_to, 'get_full_name'):
        to = [(user_or_to.get_full_name(), user_or_to.email)]
        vars['USER'] = user_or_to
    elif (isinstance(user_or_to, (list, tuple))
          and len(user_or_to) > 0
          and hasattr(user_or_to[0], 'get_full_name')):
        to = [(u.get_full_name(), u.email) for u in user_or_to]
    else:
        to = user_or_to

    context = Context(vars)
    if template_prefix:
        subject = loader.render_to_string(template_prefix + '.subject.txt', context_instance=context)
    else:
        subject = Template(subject).render(context)

    subject = CONDENSE_WHITESPACE_RE.sub(' ', subject).strip()
    context.update({'SUBJECT': subject})

    if template_prefix:
        body = loader.render_to_string(template_prefix + '.body.html', context_instance=context)
    else:
        body = Template(body).render(context)

    messages.send_mail(subject, body, to, cc=cc, bcc=bcc, frm=frm,
                       attachments=attachments, headers=headers, as_html=as_html)


def send_email_to_admins(subject=None, body=None,
                         template_prefix=None, vars=None,
                         cc=None, bcc=None, frm=None,
                         attachments=None, headers=None,
                         as_html=True):
    """
    Send an email template to the site admins.
    """
    send_email(settings.ADMINS, subject, body, template_prefix, vars, cc, bcc, frm, attachments, headers, as_html)


def send_email_to_managers(subject=None, body=None,
                           template_prefix=None, vars=None,
                           cc=None, bcc=None, frm=None,
                           attachments=None, headers=None,
                           as_html=True):
    """
    Send an email template to the site managers.
    """
    send_email(settings.MANAGERS, subject, body, template_prefix, vars, cc, bcc, frm, attachments, headers, as_html)
