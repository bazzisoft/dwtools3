from django.core.mail.backends.smtp import EmailBackend

from .settings import EmailSettings


class DebugSMTPEmailBackend(EmailBackend):
    def _send(self, email_message):
        if not EmailSettings.EMAIL_DEBUG_BACKEND_OVERRIDE_ADDRESS:
            raise RuntimeError(
                "Please configure the EMAIL_DEBUG_BACKEND_OVERRIDE_ADDRESS "
                "setting to use the DebugSMTPEmailBackend email backend."
            )

        if not email_message.recipients():
            return False

        email_message.recipients = lambda: [EmailSettings.EMAIL_DEBUG_BACKEND_OVERRIDE_ADDRESS]
        return super()._send(email_message)
