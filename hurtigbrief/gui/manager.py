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

    def submit(self, delay: float, letter: Letter, design: Design,
               template: TemplateName):
        """
        Submit a job for execution.
        """
        if self.task:
            # TODO FIXME!
            # Another task has been submitted while the old one is still
            # running. We cannot start another task on the same workspace
            # since LaTeX will overwrite the auxiliary files, and it seems
            # questionable whether we should create concurrent workspaces.
            # So, we should do one of two things:
            # 1) kill the old task and start the new one
            # 2) submit the new task to a job queue (possibly overwriting
            #    an existing submitted-but-not-started job) and run the
            #    new job as soon as the old one is done.
            #
            # Option 2) seems to be the better one. For this, we need a
            # background demon thread that starts the latex tasks,
            # waits for them to finish, sleeps, and wakes up again
            # once another task is submitted.
            # A new thread is required not to block the GUI loop while
            # waiting for the old task to finished (as it is currently
            # done in the lines below):
            warn("Waiting for an unfinished task. This should be handled "
                 "differently!")
            self.task.join()

        job = LatexTask(letter, design, template, self.workspace,
                        self.preamble_cache)
        job.notify.connect("notify_result", self.receive_result)
        self.task = job
        job.start()

    def receive_result(self, notification: Notify, result: TaskResult):
        """
        Receive the results of a task.
        """
        print("received result!")
        print("result:")
        print(result)
        self.task = None
        self.emit("notify_result", result)
