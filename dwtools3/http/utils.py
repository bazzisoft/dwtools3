import re
import time
import hashlib
from .urlparser import URLParser


_DEFAULT_SALT = 'F^u#?8idmR7G8~b=736cGnN3xz49YK=gpHu9n9?F8Ki?pG6J'
_SIGNED_URL_RE = re.compile(r'^(.*)[\?\&]sig=(\w+)&expiry=(\d+)')


def modify_url_query_string(url=None, replace=None, delete=None):
    """
    Modifies the given URL's query string by replacing or
    deleting GET parameters.

    :param str url: The URL to modify.
    :param dict replace: A dictionary of parameters to add/replace.
    :param sequence delete: A sequence of parameters to remove.

    :returns: ``str``. The updated URL.
    """
    parser = URLParser(url=url)

    if delete is not None:
        for k in delete:
            parser.query.pop(k, '')

    if replace is not None:
        parser.query.update(replace)

    return parser.build_url()


def hash_url(url, expiry, salt=None):
    """
    Calculates the hash of a given URL with specified salt and expiry timestamp.
    """
    salt = salt or _DEFAULT_SALT
    return hashlib.sha256('{}|{}|{}'.format(salt, url, expiry).encode('utf-8')).hexdigest()[::2]


def sign_url(url, expiry_secs, salt=None):
    """
    Cryptographically sign a url to ensure it's valid, not expired
    and hasn't been tampered with.
    """
    expiry = int(time.time()) + expiry_secs
    signature = hash_url(url, expiry, salt)
    divider = '&' if '?' in url else '?'
    return '{}{}sig={}&expiry={}'.format(url, divider, signature, expiry)


def verify_signed_url(url, salt=None):
    """
    Check a signed URL is valid and unexpired.
    """
    salt = salt or _DEFAULT_SALT
    m = _SIGNED_URL_RE.match(url)
    if not m:
        return None

    url = m.group(1)
    signature = m.group(2)
    expiry = int(m.group(3))

    if expiry <= int(time.time()):
        return None

    correct_signature = hash_url(url, expiry, salt)
    if signature != correct_signature:
        return None

    return url
