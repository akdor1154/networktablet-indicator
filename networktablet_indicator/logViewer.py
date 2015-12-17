from gi.repository import Gtk as gtk, GObject as gobject


class LogViewer(gtk.Dialog):

    def __init__(self, manager: 'NetworktabletIndicator', buffer: gtk.TextBuffer):
        super().__init__("Networktablet Log Viewer", None, 0)

        self.set_default_size(600, 300)

        self.manager = manager
        self.buffer = buffer
        self.scrollView = gtk.ScrolledWindow.new()

        self.textView = gtk.TextView.new_with_buffer(self.buffer)
        self.textView.set_editable(False)
        self.textView.set_cursor_visible(False)

        self.scrollView.add(self.textView)
        self.textView.connect('size-allocate', self.scroll_to_end)

        self.get_content_area().pack_start(self.scrollView, True, True, 0)

        self.add_buttons("Clear", 1, gtk.STOCK_CLOSE, gtk.ResponseType.CLOSE)

        self.connect('response', self.handle_response)

    def handle_response(self, target: gobject, response_code: int):
        if (response_code == gtk.ResponseType.CLOSE):
            self.close()
        elif (response_code == 1):
            self.clear()
        else:
            self.close()

    def scroll_to_end(self, *args):
        adj = self.scrollView.get_vadjustment()
        adj.set_value(adj.get_upper())

    def close(self):
        self.manager.dialog_closed()
        self.destroy()

    def clear(self):
        begin = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        self.buffer.delete(begin, end)
