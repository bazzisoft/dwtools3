"""
Provides enhanced email messaging such as mutlipart html/text emails.
"""
import re

from django.conf import settings
from django.core import mail as django_mail
from django.core.mail.message import EmailMultiAlternatives
from django.utils.html import strip_tags

INVISIBLE_HTML_TAGS = (
    "head",
    "style",
    "script",
    "object",
    "embed",
    "applet",
    "noframes",
    "noscript",
    "noembed",
)
INVISIBLE_HTML_TAGS_RE = [
    re.compile(r"<{tag}[^>]*?>.*?</{tag}>".format(tag=tag), re.IGNORECASE | re.DOTALL)
    for tag in INVISIBLE_HTML_TAGS
]
INVISIBLE_HTML_TAGS_RE.append(re.compile(r"<!--.*?-->", re.IGNORECASE | re.DOTALL))
INVISIBLE_HTML_TAGS_RE.append(re.compile(r"<!--.*?-->", re.IGNORECASE | re.DOTALL))
TRIM_NEWLINES_RE = re.compile(r"\n\s*\n\s*(\n\s*)+")


def strip_html_tags(message):
    for regexp in INVISIBLE_HTML_TAGS_RE:
        message = regexp.sub("", message)

    message = strip_tags(message)
    message = message.strip()

    # remove extra newlines
    message = TRIM_NEWLINES_RE.sub("\n\n", message)

    # delete spaces at the left of each line (HTML indentation)
    message = "\n".join([line.lstrip() for line in message.split("\n")])
    return message


def html_decode(s):
    """
    Returns the ASCII decoded version of the given HTML string. This does
    NOT remove normal HTML tags like <p>.
    """
    html_codes = (("'", "&#39;"), ('"', "&quot;"), (">", "&gt;"), ("<", "&lt;"), ("&", "&amp;"))

    for code in html_codes:
        s = s.replace(code[1], code[0])
    return s


class HTMLEmail(EmailMultiAlternatives):
    """
    Extends Django's EmailMultiAlternatives class to automatically
    generate a text version of a HTML email and send both the
    HTML and text versions.

    Also supports adding recipients in tuple format
    (name, email) which is correctly converted to
    name <email> format.
    """

    def __init__(
        self,
        subject="",
        body="",
        from_email=None,
        to=None,
        bcc=None,
        connection=None,
        attachments=None,
        headers=None,
        alternatives=None,
        cc=None,
        reply_to=None,
        as_html=True,
    ):
        self.as_html = as_html

        if from_email is not None:
            from_email = self.__fix_recipient_list(from_email)
            if isinstance(from_email, (list, tuple)):
                from_email = from_email[0]
        if to is not None:
            to = self.__fix_recipient_list(to)
        if cc is not None:
            cc = self.__fix_recipient_list(cc)
        if bcc is not None:
            bcc = self.__fix_recipient_list(bcc)
        if reply_to is not None:
            reply_to = self.__fix_recipient_list(reply_to)

        super(HTMLEmail, self).__init__(
            subject=subject,
            body=body,
            from_email=from_email,
            to=to,
            bcc=bcc,
            connection=connection,
            attachments=attachments,
            headers=headers,
            alternatives=alternatives,
            cc=cc,
            reply_to=reply_to,
        )

    def message(self):
        """
        Override. Returns the email message for sending by
        the email backend. Our override converts the body text
        to a MIME alternative & replaces the default body with
        a plain text version of it.
        """
        if self.as_html and self.body:
            html = self.body
            self.body = html_decode(strip_html_tags(self.body))
            self.attach_alternative(html, "text/html")

        if self.from_email:
            self.from_email = HTMLEmail.__fix_recipient_list(self.from_email)[0]

        self.to = HTMLEmail.__fix_recipient_list(self.to)
        self.cc = HTMLEmail.__fix_recipient_list(self.cc)
        self.bcc = HTMLEmail.__fix_recipient_list(self.bcc)
        self.reply_to = HTMLEmail.__fix_recipient_list(self.reply_to)

        return super(HTMLEmail, self).message()

    @staticmethod
    def __fix_recipient_list(recipients):
        """
        Updates a recipient list by checking
        for tuple/list entries and changing them to
        name <email> format.
        """
        if not recipients:
            return recipients

        if not isinstance(recipients, (tuple, list)):
            recipients = [recipients]

        newlist = []
        for recipient in recipients:
            if isinstance(recipient, (tuple, list)) and len(recipient) >= 2:
                newlist.append('"{}" <{}>'.format(recipient[0].replace('"', ""), recipient[1]))
            else:
                newlist.append(recipient)

        return newlist


def send_mail(
    subject,
    message,
    to,
    frm=None,
    cc=None,
    bcc=None,
    attachments=None,
    headers=None,
    reply_to=None,
    as_html=True,
):
    """
    Send an email per the parameters.

    If ``as_html`` is ``True``, sends a multipart email with HTML and
    plain text versions. Otherwise sends only a plain text email.

    ``attachments`` is a list of 3-tuples ``(filename, content, mimetype)``.
    """
    connection = django_mail.get_connection()

    if not as_html:
        to = [to] if isinstance(to, str) else to
        cc = [cc] if isinstance(cc, str) else cc
        bcc = [bcc] if isinstance(bcc, str) else bcc
        reply_to = [reply_to] if isinstance(reply_to, str) else reply_to

    HTMLEmail(
        subject,
        message,
        from_email=(frm or settings.DEFAULT_FROM_EMAIL),
        to=to,
        cc=cc,
        bcc=bcc,
        attachments=attachments,
        headers=headers,
        reply_to=reply_to,
        connection=connection,
        as_html=as_html,
    ).send()


def send_mass_mail(datadicts, as_html=True):
    """
    Given a list of dicts of ``{subject, message, to, frm, cc, bcc, attachments, headers}``,
    sends each message to each recipient. Returns the number of emails sent.

    If ``as_html`` is ``True``, sends a multipart email with HTML and
    plain text versions. Otherwise sends only a plain text email.

    ``attachments`` is a list of 3-tuples ``(filename, content, mimetype)``.
    """
    connection = django_mail.get_connection()

    messages = [
        HTMLEmail(
            d["subject"],
            d["message"],
            from_email=d.get("frm", settings.DEFAULT_FROM_EMAIL),
            to=d["to"],
            cc=d.get("cc"),
            bcc=d.get("bcc"),
            attachments=d.get("attachments"),
            headers=d.get("headers"),
            reply_to=d.get("reply_to"),
            connection=connection,
            as_html=as_html,
        )
        for d in datadicts
    ]
    return connection.send_messages(messages)
