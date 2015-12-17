from threading import Timer
import shlex

from gi.repository import GObject as gobject, Gtk as gtk
from gi.repository import AppIndicator3 as appindicator

from .indicatorConfig import IndicatorConfig
from .menus import IndicatorMenu
from .outputReader import OutputReader
from .logViewer import LogViewer

APPINDICATOR_ID = 'networktablet'


class NetworktabletIndicator(gobject.GObject):

    indicator = None
    thread = None

    def __init__(self):
        super().__init__()
        self.indicator = appindicator.Indicator.new(
                            APPINDICATOR_ID,
                            "input-tablet",
                            appindicator.IndicatorCategory.APPLICATION_STATUS
                        )
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

        self.config = IndicatorConfig()

        self.outputWindow = None

        self.menu = IndicatorMenu(self)
        self.indicator.set_menu(self.menu)

        self.textBuffer = gtk.TextBuffer()

        self.menu.toggleItem.set_active(self.config['enabled'])

        rootMenuItem = self.indicator \
                           .get_property('dbus-menu-server')\
                           .get_property('root-node')
        rootMenuItem.connect('about-to-show', self.menu.about_to_show)

    def handle_networktablet_output(self, output: str):
        self.debug_output(output)

    def quit(self):
        print('quitting')
        self.quit_networktablet()
        print('thread gone')
        gtk.main_quit()
        print('ghghagh')

    def networktablet_is_running(self) -> bool:
        return bool(self.thread and self.thread.is_running())

    def run_networktablet(self):
        if self.networktablet_is_running():
            self.thread.quit()
        self.thread = OutputReader(self)
        self.thread.start()
        Timer(1, self.menu.outputMenu.set_output).start()

    def quit_networktablet(self):
        if self.thread:
            self.thread.quit()

    def restart_networktablet(self):
        if self.networktablet_is_running():
            self.quit_networktablet()
            self.run_networktablet()

    def debug_output(self, output):
        if (isinstance(output, str)):
            output = output
        elif (hasattr(output, '__iter__')):
            output = ' '.join(shlex.quote(s) for s in output)+'\n'
        print(output, end="")
        end = self.textBuffer.get_end_iter()
        self.textBuffer.insert(end, output)

    def show_output(self):
        if self.outputWindow is not None:
            self.outputWindow.present()
        else:
            self.outputWindow = LogViewer(self, self.textBuffer)
            self.outputWindow.show_all()

    def dialog_closed(self):
        self.outputWindow = None
