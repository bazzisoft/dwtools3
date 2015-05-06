from .urlparser import URLParser


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

    if replace is not None:
        parser.query.update(replace)

    if delete is not None:
        for k in delete:
            parser.query.pop(k, '')

    return parser.build_url()
