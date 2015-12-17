from functools import partial
import subprocess

from gi.repository import Gtk as gtk


class ManualToggle:

    def __init__(self):
        self._lock = False

    def __enter__(self):
        self._lock = True

    def __exit__(self, *args):
        self._lock = False

    @property
    def is_active(self) -> bool:
        return self._lock


class IndicatorMenu(gtk.Menu):

    def __init__(self, manager: 'NetworktabletIndicator'):
        super().__init__()

        self.manager = manager
        self.manual_toggle = ManualToggle()

        menu_items = [
            ('Quit', self.manager.quit),
            ('Show Networktablet Output', self.manager.show_output)
        ]

        for item_data in menu_items:
            item = gtk.MenuItem(item_data[0])
            item.connect(
                'activate',
                partial(lambda f, source: f(), item_data[1])
            )
            self.append(item)

        self.toggleItem = gtk.CheckMenuItem('Enable Networktablet')
        self.toggleItem.connect('toggled', self.toggle_enable_networktablet)
        self.append(self.toggleItem)

        self.outputMenu = OutputMenu(self.manager)
        self.outputMenuItem = gtk.MenuItem('Map to Monitor')
        self.outputMenuItem.set_submenu(self.outputMenu)
        self.append(self.outputMenuItem)

        self.show_all()

    def about_to_show(self, *args):
        self.update_toggle_menuitem()
        self.outputMenu.get_networktablet_input_index()

    def toggle_enable_networktablet(self, menuItem: gtk.CheckMenuItem):
        if (self.manual_toggle.is_active):
            return

        desiredState = menuItem.get_active()
        self.manager.config['enabled'] = desiredState
        menuItem.set_inconsistent(True)

        if desiredState:
            self.manager.run_networktablet()
        else:
            self.manager.quit_networktablet()

        self.update_toggle_menuitem()

    def update_toggle_menuitem(self):
        running = self.manager.networktablet_is_running()
        with self.manual_toggle:
            self.toggleItem.set_active(running)


class Monitor:

    def __init__(self, geometry, name, index, fuzzy_position=None):
        self.width = geometry.width
        self.height = geometry.height
        self.x = geometry.x
        self.y = geometry.y
        self.name = name
        self.index = index
        self.fuzzy_position = fuzzy_position


class OutputMenu(gtk.Menu):

    def __init__(self, manager: 'NetworktabletIndicator'):
        super().__init__()
        self.manager = manager

        self.output_items = []

        self.monitors = self.get_outputs()
        self.update_items(self.monitors)

    def get_outputs(self):
        monitors = []
        self.screen = self.get_screen()
        n_monitors = self.screen.get_n_monitors()

        for n_monitor in range(n_monitors):
            geometry = self.screen.get_monitor_geometry(n_monitor)
            monitor_name = self.screen.get_monitor_plug_name(n_monitor)
            monitor = Monitor(geometry, monitor_name, n_monitor)
            monitors.append(monitor)

        monitors.sort(key=lambda m: m.x)

        if len(monitors) == 2:
            monitors[0].fuzzy_position = 'Left'
            monitors[1].fuzzy_position = 'Right'
        elif len(monitors) == 3:
            monitors[0].fuzzy_position = 'Left'
            monitors[1].fuzzy_position = 'Centre'
            monitors[2].fuzzy_position = 'Right'

        return monitors

    def update_items(self, monitors):
        self.clear_items()

        output_group = []

        all_monitors_item = gtk.RadioMenuItem.new_with_label(output_group, 'All monitors')
        output_group = all_monitors_item.get_group()
        all_monitors_item.set_active(self.manager.config['monitor'] == '')
        all_monitors_item.connect('activate', self.span_outputs_selected)
        self.append(all_monitors_item)
        self.output_items.append(all_monitors_item)

        for monitor in monitors:
            if monitor.fuzzy_position:
                label = '{0} ({1})'.format(monitor.fuzzy_position, monitor.name)
            else:
                label = monitor.name
            menu_item = gtk.RadioMenuItem.new_with_label(output_group, label)
            self.output_items.append(menu_item)
            menu_item.set_active(self.manager.config['monitor'] == monitor.name)
            menu_item.connect('activate', self.output_selected, monitor)
            self.append(menu_item)

    def clear_items(self):
        for item in self.output_items:
            item.destroy()
            self.remove(item)
        self.output_items = []

    def get_networktablet_input_index(self):
        try:
            command = ['xinput', 'list', '--id-only', 'Network Tablet']
            # self.manager.debug_output(command)
            outputBytes = subprocess.check_output(command)
        except subprocess.CalledProcessError:
            return None

        output = int(outputBytes.decode('utf-8').rstrip('\n'))
        return output

    def span_outputs_selected(self, target):
        if not target.get_active():
            return
        if self.manager.config['monitor'] != '':
            self.manager.config['monitor'] = ''
            self.manager.restart_networktablet()

    def output_selected(self, target, monitor):
        if not target.get_active():
            return
        self.manager.config['monitor'] = monitor.name
        self.set_output()

    def set_output(self):
        output_name = self.manager.config['monitor']
        if not output_name:
            return
        try:
            command = [
                'xinput',
                'map-to-output',
                str(self.get_networktablet_input_index()),
                output_name
            ]
            self.manager.debug_output(command)
            subprocess.call(command)
        except subprocess.CalledProcessError:
            pass
