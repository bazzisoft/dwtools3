import os
import time
import win32con
import win32file
import pywintypes
from .lockfilebase import LockFileBase, LockFileTimeout


class Win32LockFile(LockFileBase):
    def __init__(self, *args, **kwargs):
        super(Win32LockFile, self).__init__(*args, **kwargs)
        self.fd = None
        self.delete_lock_file = kwargs.pop('delete_lock_file', True)

    def _do_acquire(self, path, timeout):
        opts = win32con.LOCKFILE_EXCLUSIVE_LOCK if timeout < 0 else (win32con.LOCKFILE_EXCLUSIVE_LOCK | win32con.LOCKFILE_FAIL_IMMEDIATELY)
        end = time.time() + timeout

        while True:
            self.fd = open(path, 'a+b')
            hfile = win32file._get_osfhandle(self.fd.fileno())

            try:
                win32file.LockFileEx(hfile, opts, 0, -0x10000, pywintypes.OVERLAPPED())
                return self._write_pid()
            except pywintypes.error:
                self.fd.close()
                self.fd = None

            if timeout == 0 or time.time() > end:
                raise LockFileTimeout('Unable to acquire lock file {}'.format(path))

            time.sleep(timeout / 10 or 0.1)

    def _do_release(self, path):
        hfile = win32file._get_osfhandle(self.fd.fileno())
        win32file.UnlockFileEx(hfile, 0, -0x10000, pywintypes.OVERLAPPED())
        self.fd.close()
        self.fd = None
        if self.delete_lock_file:
            try:
                os.unlink(path)
            except WindowsError:
                pass

    def _write_pid(self):
        pid = os.getpid()
        #print('writing pid {}'.format(pid))
        self.fd.truncate(0)
        self.fd.write(str(pid).encode('ascii'))
        self.fd.flush()
        return True

