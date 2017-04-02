import os
import tempfile


class LockFileTimeout(Exception):
    pass


class LockFileBase(object):
    INFINITE = -1

    def __init__(self, filename=None, fullpath=None, timeout=None):
        """
        :param str fullpath: The full path to the lockfile to use.
        :param str filename: Only if fullpath is omitted. Filename to use,
            which is appended to the system temp dir.
        :param int timeout: See ``acquire``.
        """
        if fullpath:
            self.path = fullpath
        elif filename:
            self.path = os.path.join(tempfile.gettempdir(), filename)
        else:
            raise ValueError("Either 'fullpath' or 'filename' must be specified.")

        self.timeout = timeout
        self.locked = False

    def lockfile_path(self):
        return self.path

    def acquire(self, timeout=None):
        """
        Acquire the lock.

        :param int timeout: ``INFINITE`` to wait forever (default),
            ``0`` to prevent blocking, ``> 0`` to wait for ``timeout`` seconds max.

        :raise IOError: if can't open lock file.
        :raise LockFileTimeout: if can't acquire lock file in time.
        """
        if self.locked:
            return True

        if timeout is None:
            timeout = self.timeout if self.timeout is not None else self.INFINITE
        elif timeout < 0:
            timeout = self.INFINITE

        if self._do_acquire(self.path, timeout):
            self.locked = True

    def release(self):
        if self.locked:
            self._do_release(self.path)
            self.locked = False

    def _do_acquire(self, path, timeout):
        raise NotImplementedError()

    def _do_release(self, path):
        raise NotImplementedError()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
