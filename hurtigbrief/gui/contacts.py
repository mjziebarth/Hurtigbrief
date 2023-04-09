# Contact dialog.
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

from .gtk import Gtk, GObject
from ..abstraction.address import Address, GermanAddress
from ..abstraction.person import Person
from typing import List


class ContactsDialog(Gtk.Dialog):
    """
    A dialog showing the contact information.
    """

    __gsignals__ = {
        "person_changed" : (GObject.SIGNAL_RUN_FIRST, None,
                            (object,))
    }

    def __init__(self, parent, address_type=GermanAddress):
        super().__init__(title="Contacts", transient_for=parent)

        self.address_type = address_type

        self.people_model = Gtk.ListStore(str, str, str, str)
        self.people_view = Gtk.TreeView(model=self.people_model,
                                        headers_visible=True)
        self.people_view.set_hexpand(True)
        self.people_view.set_vexpand(True)

        # The columns to display
        # 1) Name
        renderer = Gtk.CellRendererText(editable=True)
        renderer.connect("edited", self.name_edited)
        column = Gtk.TreeViewColumn("Name", renderer, text=0, weight=1)
        column.set_expand(True)
        self.people_view.append_column(column)

        # 2) Address
        renderer = Gtk.CellRendererText(editable=True)
        renderer.connect("edited", self.address_edited)
        column = Gtk.TreeViewColumn("Address", renderer, text=1, weight=1)
        column.set_expand(True)
        self.people_view.append_column(column)

        # 3) E-Mail
        renderer = Gtk.CellRendererText(editable=True)
        renderer.connect("edited", self.email_edited)
        column = Gtk.TreeViewColumn("E-Mail", renderer, text=2, weight=1)
        column.set_expand(True)
        self.people_view.append_column(column)

        # 4) Phone
        renderer = Gtk.CellRendererText(editable=True)
        renderer.connect("edited", self.phone_edited)
        column = Gtk.TreeViewColumn("Phone", renderer, text=3, weight=1)
        column.set_expand(True)
        self.people_view.append_column(column)


        layout = Gtk.Grid()
        layout.attach(Gtk.Label("Contacts:"), 0, 0, 1, 1)
        layout.attach(self.people_view, 0, 1, 1, 1)
        self.get_content_area().add(layout)
        self.show_all()


    def update_person(self, row: int) -> bool:
        """
        Store the person at 'row'.
        """
        # Get the data saved in the row:
        if row >= self.people_model.iter_n_children():
            raise RuntimeError("Row out of bounds.")

        it = self.people_model.get_iter(row)
        name_s = self.people_model.get(it, 0)[0]
        addr_s = self.people_model.get(it, 1)[0]
        email_s = self.people_model.get(it, 2)[0]
        phone_s = self.people_model.get(it, 3)[0]

        # Try to construct the address:
        try:
            address = self.address_type.parse_address(addr_s)
        except:
            # Return early (this person needs more editing before we allow
            # its creation into the people list)
            return False

        # See if the address is known:
        if address in self.a2i:
            i = self.a2i[address]
        else:
            # Unknown, create new:
            i = len(self.addresses)
            self.addresses.append(address)
            self.a2i[address] = i

        # Create the new person:
        p = Person(name_s, self.addresses[i], email_s, phone_s)
        if row == len(self.people):
            self.people.append(p)
        else:
            self.people[row] = p

        return True


    def edited(self, row, col, new_text):
        """
        General edited call.
        """
        is_new_row = row + 1 == self.people_model.iter_n_children()

        # Update the model:
        it = self.people_model.get_iter(row)
        self.people_model.set(it, col, new_text)

        # Update the person:
        if not self.update_person(row):
            # Edit did not lead to a valid person!
            return

        # If the last, empty row is edited, add a new row:
        if is_new_row:
            self.people_model.append(("","","",""))

        # This person changed!
        self.emit("person_changed", row)


    def name_edited(self, *args):
        row = int(args[1])
        new_text = args[2]
        self.edited(row, 0, new_text)


    def address_edited(self, *args):
        row = int(args[1])
        new_text = args[2]
        self.edited(row, 1, new_text)


    def email_edited(self, *args):
        # If the last, empty row is edited, add a new row:
        row = int(args[1])
        new_text = args[2]
        self.edited(row, 2, new_text)


    def phone_edited(self, *args):
        # If the last, empty row is edited, add a new row:
        row = int(args[1])
        new_text = args[2]
        self.edited(row, 3, new_text)


    def set_data(self, addresses: List[Address], people: List[Person]):
        """
        Register the contact 'data base'.
        """
        self.addresses = addresses
        self.people = people
        address_indices = []
        a2i = {a : i for i,a in enumerate(addresses)}
        for person in self.people:
            i = a2i[person.address]
            addr = ", ".join(person.address.compose())
            self.people_model.append((person.name, addr,
                                      person.email, person.phone))
            address_indices.append(i)
        self.address_indices = address_indices
        self.a2i = a2i

        # Add the editable final row:
        self.people_model.append(("","","",""))
