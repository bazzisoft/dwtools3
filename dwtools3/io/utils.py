import sys
import codecs


def create_console_string_writer(stream=None, encoding='utf-8'):
    """
    Creates a StreamWriter object that writes strings to the
    specified console stream, with the given encoding.

    :param stream: Defaults to ``sys.stdout``.
    :param str encoding: Defaults to ``'utf-8'``.
    """
    stream = stream or sys.stdout
    return codecs.getwriter(encoding)(stream.buffer)
