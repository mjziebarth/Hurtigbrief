# The main window.
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

from .gtk import Gtk, GtkSource, EvinceView
from .config import default
from ..abstraction.address import address_from_json
from ..abstraction.person import Person
from ..abstraction.letter import Letter
from typing import Optional

class HurtigbriefWindow(Gtk.ApplicationWindow):
    """
    The window.
    """
    default_sender: Optional[int]

    def __init__(self, application=None):
        super().__init__(application=application)

        # Some variables:
        self.addresses = [address_from_json(json)
                          for json in default["addresses"]]
        self.people = [Person.from_json(json, self.addresses)
                       for json in default["people"]]
        default_sender = int(default["default_sender"])
        if default_sender >= 0 and default_sender < len(self.people):
            self.sender = default_sender
        else:
            self.sender = None
        print("addresses:", self.addresses)

        # TODO fixme!
        self.destination = 1


        # Layout
        layout = Gtk.HPaned()
        layout_left = Gtk.Grid()
        layout.add1(layout_left)

        # The addresses:
        label_sender = Gtk.Label('From:', halign=Gtk.Align.START)
        layout_left.attach(label_sender, 0, 0, 1, 1)
        label_destination = Gtk.Label('To:', halign=Gtk.Align.START)
        layout_left.attach(label_destination, 0, 1, 1, 1)

        # The subject:
        try:
            languages = GtkSource.LanguageManager()
            language = languages.get_language('latex')
        except:
            language = None
        self.subject_buffer = GtkSource.Buffer(language=language)
        self.subject_edit = GtkSource.View(buffer=self.subject_buffer)
        layout_left.attach(self.subject_edit, 0, 2, 2, 1)

        # The opening:
        self.opening_buffer = GtkSource.Buffer(language=language)
        self.opening_buffer.set_text(default['opening'])
        self.opening_edit = GtkSource.View(buffer=self.opening_buffer)
        layout_left.attach(self.opening_edit, 0, 3, 2, 1)

        # The main body text source view:
        bodyscroll = Gtk.ScrolledWindow()
        self.body_buffer = GtkSource.Buffer(language=language)
        self.body_edit = GtkSource.View(buffer=self.body_buffer, expand = True)
        bodyscroll.add(self.body_edit)
        layout_left.attach(bodyscroll, 0, 4, 2, 1)

        # The closing:
        self.closing_buffer = GtkSource.Buffer(language=language)
        self.closing_buffer.set_text(default['closing'])
        self.closing_edit = GtkSource.View(buffer=self.closing_buffer)
        layout_left.attach(self.closing_edit, 0, 5, 2, 1)

        # The PDF view:
        self.pdf_view = EvinceView.View(expand = True)
        evscroll = Gtk.ScrolledWindow()
        evscroll.add(self.pdf_view)
        layout.add2(evscroll)

        run_button = Gtk.Button("Go!")
        layout_left.attach(run_button, 0, 6, 1, 1)
        run_button.connect("clicked", lambda btn : self.generate_letter())

        self.add(layout)

        self.show_all()

        # Get a hopefully DPI-aware height measure from the
        # drawn label:
        font_height = label_sender.get_allocated_height()

        layout_left.set_row_spacing(max(round(0.2*font_height), 1))

    def generate_letter(self) -> Letter:
        """
        Generates the letter from the current content.
        """
        sender = self.people[self.sender]
        destination = self.people[self.destination]
        subject = self.subject_buffer.get_text(
            self.subject_buffer.get_start_iter(),
            self.subject_buffer.get_end_iter(),
            False
        )
        opening = self.opening_buffer.get_text(
            self.opening_buffer.get_start_iter(),
            self.opening_buffer.get_end_iter(),
            False
        )
        body = self.body_buffer.get_text(
            self.body_buffer.get_start_iter(),
            self.body_buffer.get_end_iter(),
            False
        )
        closing = self.closing_buffer.get_text(
            self.closing_buffer.get_start_iter(),
            self.closing_buffer.get_end_iter(),
            False
        )
        return Letter(sender, destination, subject, opening, body, closing)
