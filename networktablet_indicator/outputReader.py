from threading import Thread, Lock
import pty
import subprocess
import os

from gi.repository import GLib as glib


networktablet_command = 'networktablet'


class OutputReader(Thread):

    _p = None

    def __init__(self, manager: 'NetworktabletIndicator', **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.starting_lock = Lock()

    def run(self):
        with self.starting_lock:
            self.master, self.slave = pty.openpty()

            self._p = subprocess.Popen(
                                    args=networktablet_command.split(' '),
                                    stdout=self.slave,
                                    stderr=self.slave,
                                    bufsize=0,
                                    shell=False,
                                    close_fds=True)
            self.process_output = os.fdopen(self.master)

        try:
            while not self.process_output.closed:
                line = self.process_output.readline()
                self.add_output(line)
        except ValueError:
            pass
        except OSError:
            pass

        self.process_output.close()

    def add_output(self, line):
        glib.idle_add(self.manager.handle_networktablet_output, line)

    def is_running(self) -> bool:
        with self.starting_lock:
            return self._p and (self._p.poll() is None)

    def quit(self):
        if self.is_running():
            print('waiting for lock')
            with self.starting_lock:
                print('killing')
                self._p.terminate()
                print('waiting')
                self._p.wait()
                print('dead')
                os.close(self.slave)
        else:
            self._p.wait()
            os.close(self.slave)
