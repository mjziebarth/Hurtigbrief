# A latex task.
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

from ..abstraction.letter import Letter
from ..abstraction.design import Design
from ..latex.mklatex import do_latex
from ..latex.workspace import Workspace
from ..latex.preamblecache import PreambleCache
from .types import TemplateName
from .gtk import GObject
from .notify import Notify
from threading import Thread

class LatexTask(Thread):
    """
    A latex compilation job executed in a separate thread.
    """
    def __init__(self, letter: Letter, design: Design, template: TemplateName,
                 workspace: Workspace, preamble_cache: PreambleCache):
        super().__init__(daemon=True)
        self.letter = letter
        self.design = design
        self.template = template
        self.workspace = workspace
        self.preamble_cache = preamble_cache
        self.notify = Notify()

    def run(self):
        do_latex(self.letter, self.design, self.template, self.workspace,
                 self.preamble_cache)
        self.notify.emit_result("The result")
