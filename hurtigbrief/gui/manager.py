# Task manager
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

from .task import LatexTask, TaskResult
from .gtk import GObject
from .types import TemplateName
from .notify import Notify
from ..abstraction import Letter, Design
from ..latex.workspace import Workspace
from ..latex.preamblecache import PreambleCache
from typing import Optional
from warnings import warn
from threading import Thread
from queue import Queue

class TaskLoop(Thread):
    """
    A loop that receives jobs and starts latex tasks one at a time.
    """
    def __init__(self, queue: Queue, manager: "TaskManager",
                 workspace: Workspace, preamble_cache: PreambleCache):
        # Set it as a daemon thread:
        super().__init__(daemon=True)
        self.notify = Notify()
        self.queue = queue
        self.manager = manager
        self.workspace = workspace
        self.preamble_cache = preamble_cache

    def run(self):
        while True:
            # Get a new job, the most recent entry in the job queue:
            letter, design, template = self.queue.get()
            while not self.queue.empty():
                self.queue.task_done()
                letter, design, template = self.queue.get()

            # Start a new task and wait for it to finish:
            job = LatexTask(letter, design, template, self.workspace,
                            self.preamble_cache)
            job.notify.connect("notify_result", self.manager.receive_result)
            job.start()
            job.join()

            # Finish that task.
            self.queue.task_done()


class TaskManager(GObject.GObject):
    """
    Manage the LaTeX task(s).
    """
    task: Optional[LatexTask]

    __gsignals__ = {
        "notify_result" : (GObject.SIGNAL_RUN_FIRST, None, (object,))
    }

    def __init__(self, workspace: Workspace, preamble_cache: PreambleCache):
        super().__init__()
        self.task = None
        self.workspace = workspace
        self.preamble_cache = preamble_cache
        self.queue = Queue()
        self.task_loop = TaskLoop(self.queue, self, workspace, preamble_cache)
        self.task_loop.start()

    def submit(self, delay: float, letter: Letter, design: Design,
               template: TemplateName):
        """
        Submit a job for execution.
        """
        self.queue.put((letter, design, template))

    def receive_result(self, notification: Notify, result: TaskResult):
        """
        Receive the results of a task.
        """
        self.task = None
        self.emit("notify_result", result)
