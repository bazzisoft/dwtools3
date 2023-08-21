from __future__ import absolute_import
import io
import os
import time
import threading
from tempfile import NamedTemporaryFile


_compat_named_temporary_file_lock = threading.Lock()
_compat_named_temporary_file_list = []


class CompatNamedTemporaryFile(object):
    """
    A cross-platform version of ``NamedTemporaryFile`` which is closed after
    every open/read/write operation for compatibility with Windows NT and later.

    Since the temporary files are not deleted on close provides a method
    to cleanup any lingering tempfiles on disk (older than X secs).

    NOTE: This only supports a small subset of the file-like operations
    available on the regular ``NamedTemporaryFile``. It doesn't support usage
    as a context manager as the file will never get deleted. Use the regular
    ``NamedTemporaryFile`` for this in a ``try...finally`` block to unlink
    the file at the end.
    """

    def __init__(
        self,
        mode="w+b",
        buffering=-1,
        encoding=None,
        newline=None,
        suffix="",
        prefix="tmp",
        dir=None,
        delete=True,
    ):
        self._tmpfile = NamedTemporaryFile(
            mode, buffering, encoding, newline, suffix, prefix, dir, delete=False
        )
        self._tmpfile.close()
        self._created_at = time.time()
        self._name = self._tmpfile.name
        self._mode = "r+b" if mode.endswith("b") else "r+"
        self._buffering = buffering
        self._encoding = encoding
        self._newline = newline
        self._fd = None

        with _compat_named_temporary_file_lock:
            _compat_named_temporary_file_list.append(self)

    @property
    def name(self):
        return self._name

    def _reopen(self, at_end=False):
        if self._fd is None:
            self._fd = open(
                self._tmpfile.name,
                self._mode,
                buffering=self._buffering,
                encoding=self._encoding,
                newline=self._newline,
            )
            if at_end:
                self._fd.seek(0, io.SEEK_END)
        return self._fd

    def _reclose(self):
        if self._fd:
            self._fd.close()
            self._fd = None

    def read(self, size=-1):
        self._reopen()
        try:
            return self._fd.read(size)
        finally:
            self._reclose()

    def write(self, str):
        self._reopen(at_end=True)
        try:
            return self._fd.write(str)
        finally:
            self._reclose()

    def seek(self, offset, whence=io.SEEK_SET):
        if offset != 0 or whence != io.SEEK_SET:
            self._reopen()
            self._fd.seek(offset, whence)
        else:
            self._reclose()

    def flush(self):
        self._reclose()

    def close(self):
        self._reclose()

    def delete(self):
        self._reclose()
        try:
            os.unlink(self._name)
        except:
            pass

    @staticmethod
    def cleanup_lingering_tempfiles(age=0):
        """
        Cleans up any lingering tempfiles, older than ``age`` seconds,
        by unlinking them from the system.
        """
        if not _compat_named_temporary_file_lock.acquire():
            return

        try:
            t = time.time() - age
            while (
                len(_compat_named_temporary_file_list)
                and _compat_named_temporary_file_list[0]._created_at < t
            ):
                _compat_named_temporary_file_list.pop(0).delete()
        finally:
            _compat_named_temporary_file_lock.release()

    @staticmethod
    def start_cleanup_thread(age=0, every=30):
        """
        Starts a thread that tries to cleanup any lingering tempfiles older than ``age``
        seconds by unlinking them from the system. Checks for lingering tempfiles
        once per 30 seconds.
        """

        def try_cleanup():
            while True:
                time.sleep(every)
                CompatNamedTemporaryFile.cleanup_lingering_tempfiles(age)

        t = threading.Thread(target=try_cleanup)
        t.daemon = True
        t.start()
