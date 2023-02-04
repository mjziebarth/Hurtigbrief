# The main application, running the main window and performing the
# latex compilation.
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
from ..abstraction import Letter, Design
from typing import Literal
from hurtigbrief.latex.mklatex import do_latex
from hurtigbrief.latex.workspace import Workspace
from hurtigbrief.latex.preamblecache import PreambleCache

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

    def on_activate(self):
        win = HurtigbriefWindow(application=self)
        win.present()

    def on_letter_changed(self, letter: Letter, design: Design,
                          template: Literal["scrletter"]):
        """
        This method compiles the letter.
        """
        do_latex(letter, design, "scrletter", self.workspace,
                 self.preamble_cache)
