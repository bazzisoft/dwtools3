"""
Provides file-based locking for linux and windows platforms.


Dependencies
------------
On windows, you need to install the ``pypiwin32`` package.


Usage
-----
::

    from dwtools3.system.lockfile import LockFile, LockFileTimeout, lock_file

    # Will wait forever to lock, lockfile placed in temp dir
    @lock_file('mylock.lck', timeout=LockFile.INFINITE)
    def my_func1():
        pass


    # Will wait 10 secs to acquire lock, raising LockFileTimeout if fails.
    # Full path to lock file specified.
    def my_func2():
        with LockFile(fullpath='/tmp/mylock.lck', timeout=10):
            pass


    # Will not block.
    def my_func3():
        lock = LockFile('mylock.lck', timeout=0)
        try:
            lock.acquire()
            do_something()
            lock.release()
        except LockFileTimeout as e:
            pass
"""

LockFile = None


def _prepare_lockfile():
    global LockFile
    import os

    if os.name != "nt":
        from . import pidlockfile

        LockFile = pidlockfile.PIDLockFile
    else:
        from . import win32lockfile

        LockFile = win32lockfile.Win32LockFile


_prepare_lockfile()


def lock_file(filename=None, fullpath=None, timeout=None):
    from functools import wraps

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            with LockFile(filename=filename, fullpath=fullpath, timeout=timeout):
                return fn(*args, **kwargs)

        return wrapper

    return decorator
