# The main application, running the main window and performing the
# latex compilation.
#
# Author: Malte J. Ziebarth (mjz.science@fmvkb.de)
#
# Copyright (C) 2023 Malte J. Ziebarth
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from .gtk import Gtk
from .window import HurtigbriefWindow
from .scheduler import Scheduler
from .types import TemplateName
from .manager import TaskManager
from ..abstraction import Letter, Design
from ..latex.workspace import Workspace
from ..latex.preamblecache import PreambleCache

class HurtigbriefApp(Gtk.Application):
    """
    The main Hurtigbrief app.
    """
    def __init__(self):
        super().__init__(application_id='app.Hurtigbrief')
        self.connect('activate', HurtigbriefApp.on_activate)
        print("finished initialization!")
        self.workspace = Workspace()
        self.preamble_cache = PreambleCache(self.workspace)
        self.task_manager = TaskManager(self.workspace, self.preamble_cache)
        self.scheduler = Scheduler()

    def on_activate(self):
        self.window = HurtigbriefWindow(application=self)
        self.window.connect("letter_changed", self.on_letter_changed)
        self.window.present()

    def on_letter_changed(self, window: HurtigbriefWindow, letter: Letter,
                          design: Design, template: TemplateName):
        """
        This method compiles the letter.
        """
        delay_seconds =  self.scheduler.propose_delay()
        self.task_manager.submit(delay_seconds, letter, design, template)
