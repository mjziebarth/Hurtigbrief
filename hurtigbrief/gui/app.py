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
from .task import TaskResult
from ..abstraction import Letter, Design
from ..latex.workspace import Workspace
from ..latex.preamblecache import PreambleCache
from datetime import datetime

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
        self.task_manager.connect("notify_result", self.on_receive_result)
        self.task_manager.connect("notify_compile_time",
                                  self.on_receive_compile_time)
        self.scheduler = Scheduler()
        self.document = None
        # Measure the time since the last document change:
        self.lastchange = None

    def on_activate(self):
        self.window = HurtigbriefWindow(application=self)
        self.window.connect("letter_changed", self.on_letter_changed)
        self.window.present()

    def on_letter_changed(self, window: HurtigbriefWindow, letter: Letter,
                          design: Design, template: TemplateName):
        """
        This method compiles the letter.
        """
        # Measure the time since the last change:
        now = datetime.now()
        if self.lastchange is not None:
            dt = (now - self.lastchange).total_seconds()
            self.scheduler.register_keystroke_waiting_time(dt)
        self.lastchange = now
        delay_seconds =  self.scheduler.propose_delay()
        self.task_manager.submit(delay_seconds, letter, design, template)

    def on_receive_result(self, manager: TaskManager, result: TaskResult):
        """
        Receive the result of a latex compilation.
        """
        self.window.on_receive_result(result)

    def on_receive_compile_time(self, compile_time: float):
        """
        Receive the runtime of the LaTeX compilation in seconds.
        """
        self.scheduler.register_compile_time(compile_time)
