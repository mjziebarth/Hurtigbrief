# Notification from finished threads.
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

from .gtk import GObject

class Notify(GObject.GObject):
    """
    A class to notify, from a different Python thread, the main
    application about the completion and result of a task.
    """
    __gsignals__ = {
        "notify_result" : (GObject.SIGNAL_RUN_FIRST, None, (object,)),
        "notify_compile_time" : (GObject.SIGNAL_RUN_FIRST, None, (object,))
    }

    def __init__(self):
        super().__init__()

    def emit_result(self, result):
        self.emit("notify_result", result)

    def emit_compile_time(self, compile_time: float):
        self.emit("notify_compile_time", compile_time)
