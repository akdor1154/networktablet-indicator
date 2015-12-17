from gi.repository import Gtk as gtk, GLib as glib
import signal

from networktablet_indicator.indicator import NetworktabletIndicator


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    glib.threads_init()

    app = NetworktabletIndicator()
    gtk.main()
