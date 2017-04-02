import os
import time
import fcntl
from .lockfilebase import LockFileBase, LockFileTimeout


class PIDLockFile(LockFileBase):
    def __init__(self, *args, **kwargs):
        super(PIDLockFile, self).__init__(*args, **kwargs)
        self.fd = None
        self.delete_lock_file = kwargs.pop('delete_lock_file', True)

    def _do_acquire(self, path, timeout):
        opts = fcntl.LOCK_EX if timeout < 0 else (fcntl.LOCK_EX | fcntl.LOCK_NB)
        end = time.time() + timeout

        while True:
            self.fd = open(path, 'a+b')

            try:
                fcntl.flock(self.fd, opts)
                return self._write_pid()
            except IOError:
                self.fd.close()
                self.fd = None

            if timeout == 0 or time.time() > end:
                raise LockFileTimeout('Unable to acquire lock file {}'.format(path))

            time.sleep(timeout / 10 or 0.1)

    def _do_release(self, path):
        self.fd.close()
        self.fd = None
        if self.delete_lock_file:
            self._delete_lock_file(path)

    def _write_pid(self):
        pid = os.getpid()
        #print('writing pid {}'.format(pid))
        self.fd.truncate(0)
        self.fd.write(str(pid).encode('ascii'))
        self.fd.flush()
        return True

    def _delete_lock_file(self, path):
        # Give another process a change to capture the lock
        time.sleep(0.1)
        with open(path, 'a+b') as tmpfd:
            try:
                fcntl.flock(tmpfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                try:
                    os.unlink(path)
                    #print('deleted.')
                except OSError:
                    #print('delete failed.')
                    pass
            except IOError:
                #print('cant delete.')
                pass
