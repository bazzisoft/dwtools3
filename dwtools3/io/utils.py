import sys
import codecs
import pprint


def create_console_string_writer(stream=None, encoding='utf-8'):
    """
    Creates a StreamWriter object that writes strings to the
    specified console stream, with the given encoding.

    :param stream: Defaults to ``sys.stdout``.
    :param str encoding: Defaults to ``'utf-8'``.
    """
    stream = stream or sys.stdout
    return codecs.getwriter(encoding)(stream.buffer)


def pprint_unicode_to_console(s, end='\n'):
    writer = create_console_string_writer()
    writer.write(pprint.pformat(s, indent=2))
    if end:
        writer.write(end)
