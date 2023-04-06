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

from .gtk import Gtk
from ..abstraction.address import Address
from ..abstraction.person import Person
from typing import List


class ContactsDialog(Gtk.Dialog):
    """
    A dialog showing the contact information.
    """
    def __init__(self, parent):
        super().__init__(title="Contacts", transient_for=parent)
        self.people_model = Gtk.ListStore(str, str, str, str)
        self.people_view = Gtk.TreeView(model=self.people_model,
                                        headers_visible=True)
        self.people_view.set_hexpand(True)
        self.people_view.set_vexpand(True)
        print(self.people_model.get_n_columns())
        print(self.people_view.get_columns())

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


    def name_edited(self, *args):
        # If the last, empty row is edited, add a new row:
        row = int(args[1])
        if row + 1 == self.people_model.iter_n_children():
            self.people_model.append(("","","",""))
        print("Name edited:", args)


    def address_edited(self, *args):
        # If the last, empty row is edited, add a new row:
        row = int(args[1])
        if row + 1 == self.people_model.iter_n_children():
            self.people_model.append(("","","",""))

        print("Address edited:", args)


    def email_edited(self, *args):
        # If the last, empty row is edited, add a new row:
        row = int(args[1])
        if row + 1 == self.people_model.iter_n_children():
            self.people_model.append(("","","",""))

        print("Email edited:", args)


    def phone_edited(self, *args):
        # If the last, empty row is edited, add a new row:
        row = int(args[1])
        if row + 1 == self.people_model.iter_n_children():
            self.people_model.append(("","","",""))

        print("Phone edited:", args)


    def set_data(self, addresses: List[Address], people: List[Person]):
        """
        Register the contact 'data base'.
        """
        self.addresses = addresses
        self.people = people
        address_indices = []
        a2i = {id(a) : i for i,a in enumerate(addresses)}
        for person in self.people:
            i = a2i[id(person.address)]
            addr = ", ".join(person.address.compose())
            self.people_model.append((person.name, addr,
                                      person.email, person.phone))
        self.address_indices = address_indices
        self.people_model.append(("","","",""))
