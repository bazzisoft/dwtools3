import urllib.parse
from collections import OrderedDict


class URLParser:
    """
    Class to parse URLs into parts, allowing you to modify them & build
    the modified URL anew.

    Constructor splits the URL given by the url string or request.

    :param str url: The URL to parse.
    """
    def __init__(self, url):
        ret = urllib.parse.urlparse(url)

        self.protocol = ret.scheme or ''
        """eg. ``http``, ``https``"""

        self.username = ret.username or ''
        """eg. ``http://joe:secret@foo.com/  =>  joe``"""

        self.password = ret.password or ''
        """eg. ``http://joe:secret@foo.com/  =>  secret``"""

        self.hostname = ret.hostname or ''
        """eg. ``foo.com``"""

        self.port = ret.port or ''
        """eg. ``http://foo.com:8080/  =>  8080``"""

        self.path = ret.path or ''
        """eg. ``/path/to/content/``"""

        self.query = None
        """OrderedDict of name-value pair GET parameters."""

        self.fragment = ret.fragment or ''
        """eg. ``http://foo.com/page/#contents  =>  contents``"""

        # Parse the query string into self.query
        self.query_string = ret.query

    @property
    def query_string(self):
        """
        ``str``. Returns the query string by combining ``self.query`` into a query string,
        or splits the query string assigned to it into the ``self.query`` dictionary.
        """
        return urllib.parse.urlencode(self.query)

    @query_string.setter
    def query_string(self, value):
        self.query = OrderedDict(urllib.parse.parse_qsl(value, keep_blank_values=True))

    def build_url(self):
        """
        Builds a full URL from the split components.
        """
        userstring = ''
        if self.username:
            userstring += self.username
            if self.password:
                userstring += ':' + self.password
            userstring += '@'

        portstring = ':{}'.format(self.port) if self.port else ''
        netloc = userstring + self.hostname + portstring

        return urllib.parse.urlunparse(
            (self.protocol, netloc, self.path, None, self.query_string, self.fragment))

    def __str__(self):
        return self.build_url()
