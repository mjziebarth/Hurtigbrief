# The main window.
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

from .gtk import Gtk, GtkSource, EvinceView, GObject, EvinceDocument
from .config import default, save_contacts
from .types import TemplateName
from .task import TaskResult
from .contacts import ContactsDialog
from ..abstraction.address import address_from_json
from ..abstraction.person import Person
from ..abstraction.letter import Letter
from ..abstraction.design import Design
from typing import Optional
from importlib.resources import files
from pathlib import Path
from shutil import copyfile
import json


class HurtigbriefWindow(Gtk.ApplicationWindow):
    """
    The window.
    """
    default_sender: Optional[int]

    __gsignals__ = {
        "letter_changed" : (GObject.SIGNAL_RUN_FIRST, None,
                            (object, object, object))
    }

    def __init__(self, application=None):
        super().__init__(application=application)

        # Some variables:
        self.addresses = [address_from_json(json)
                          for json in default["addresses"]]
        self.people = [Person.from_json(json, self.addresses)
                       for json in default["people"]]
        self.p2i = {p : i for i,p in enumerate(self.people)}
        default_sender = default["default_sender"]
        if default_sender is not None:
            default_sender = int(default_sender)
            if default_sender >= 0 and default_sender < len(self.people):
                self.sender = default_sender
            else:
                self.sender = None
        else:
            self.sender = None
        self.default_sender = default_sender
        print("addresses:", self.addresses)

        # Use this information to enable or disable the 'Save Contacts'
        # button:
        self.contacts_hash = self.compute_contacts_hash()

        self.document_path = None
        self.document = None

        # No default destination for a new letter.
        self.destination = None

        # The signal handlers that react on changed GUI components
        # (we need to deactivate them when loading a letter so as not to
        # trigger too many calls to generate_letter at the same time)
        self.gui_handlers = dict()

        # Header bar:
        icon_load_letter = Gtk.Image.new_from_file(
             str(files('hurtigbrief.gui.icons').joinpath('load-letter.svg'))
        )
        icon_letter = Gtk.Image.new_from_file(
             str(files('hurtigbrief.gui.icons').joinpath('save-letter.svg'))
        )
        icon_pdf = Gtk.Image.new_from_file(
             str(files('hurtigbrief.gui.icons').joinpath('save-pdf.svg'))
        )
        icon_contacts = Gtk.Image.new_from_file(
             str(files('hurtigbrief.gui.icons').joinpath('save-contacts.svg'))
        )
        self.header_bar = Gtk.HeaderBar(title="Hurtigbrief")
        self.header_bar.set_show_close_button(True)
        self.load_letter_button = Gtk.Button(tooltip_text='Load letter')
        self.load_letter_button.set_image(icon_load_letter)
        self.load_letter_button.connect("clicked", self.on_load_letter_clicked)
        self.save_letter_button = Gtk.Button(tooltip_text='Save letter')
        self.save_letter_button.set_image(icon_letter)
        self.save_letter_button.connect("clicked", self.on_save_letter_clicked)
        self.save_pdf_button = Gtk.Button(tooltip_text='Save PDF')
        self.save_pdf_button.set_image(icon_pdf)
        self.save_pdf_button.set_sensitive(False)
        self.save_pdf_button.connect("clicked", self.on_save_pdf_clicked)
        self.save_contacts_button = Gtk.Button(tooltip_text='Save contacts')
        self.save_contacts_button.set_image(icon_contacts)
        self.save_contacts_button.set_sensitive(False)
        self.save_contacts_button.connect("clicked",
                                          self.on_save_contacts_clicked)
        self.header_bar.pack_start(self.load_letter_button)
        self.header_bar.pack_start(self.save_letter_button)
        self.header_bar.pack_start(self.save_pdf_button)
        self.header_bar.pack_start(self.save_contacts_button)
        self.set_titlebar(self.header_bar)

        # Save dialogs:
        self.letter_save_path = None
        self.pdf_save_path = None


        # Layout
        layout = Gtk.HPaned()
        layout_left = Gtk.Grid(column_homogeneous=False)
        layout.add1(layout_left)

        # The addresses:
        self.name_model = self.generate_contact_list_model()
        label_sender = Gtk.Label('From:', halign=Gtk.Align.START)
        layout_left.attach(label_sender, 0, 0, 1, 1)
        self.cb_sender = Gtk.ComboBox.new_with_model(self.name_model)
        renderer = Gtk.CellRendererText()
        self.cb_sender.pack_start(renderer, True)
        self.cb_sender.add_attribute(renderer, 'text', 0)
        if self.sender is not None:
            self.cb_sender.set_active(self.sender)
        layout_left.attach(self.cb_sender, 1, 0, 1, 1)
        label_destination = Gtk.Label('To:', halign=Gtk.Align.START)
        layout_left.attach(label_destination, 0, 1, 1, 1)
        self.cb_destination = Gtk.ComboBox.new_with_model(self.name_model)
        h0 = self.cb_destination.connect("changed", self.on_letter_changed)
        self.gui_handlers[id(self.cb_destination)] = h0
        h1 = self.cb_sender.connect("changed", self.on_letter_changed)
        self.gui_handlers[id(self.cb_sender)] = h1
        renderer = Gtk.CellRendererText()
        self.cb_destination.pack_start(renderer, True)
        self.cb_destination.add_attribute(renderer, 'text', 0)
        layout_left.attach(self.cb_destination, 1, 1, 1, 1)

        # The address book:
        address_button = Gtk.Button.new_from_icon_name(
            "contact-new",
            Gtk.IconSize.BUTTON
        )
        layout_left.attach(address_button, 2, 0, 1, 2)
        address_button.set_halign(Gtk.Align.START)
        address_button.set_valign(Gtk.Align.CENTER)
        address_button.connect("clicked", self.show_address_dialog)

        # Eat space:
        space_eater = Gtk.Label("")
        layout_left.attach(space_eater, 3, 0, 1, 2)
        space_eater.set_hexpand(True)

        # The subject:
        try:
            languages = GtkSource.LanguageManager()
            language = languages.get_language('latex')
        except:
            language = None
        self.subject_buffer = GtkSource.Buffer(language=language)
        h2 = self.subject_buffer.connect('changed', self.on_letter_changed)
        self.gui_handlers[id(self.subject_buffer)] = h2
        self.subject_edit = GtkSource.View(buffer=self.subject_buffer)
        layout_left.attach(self.subject_edit, 0, 2, 4, 1)

        # The opening:
        self.opening_buffer = GtkSource.Buffer(language=language)
        self.opening_buffer.set_text(default['opening'])
        h3 = self.opening_buffer.connect('changed', self.on_letter_changed)
        self.gui_handlers[id(self.opening_buffer)] = h3
        self.opening_edit = GtkSource.View(buffer=self.opening_buffer)
        layout_left.attach(self.opening_edit, 0, 3, 4, 1)

        # The main body text source view:
        bodyscroll = Gtk.ScrolledWindow()
        self.body_buffer = GtkSource.Buffer(language=language)
        h4 = self.body_buffer.connect('changed', self.on_letter_changed)
        self.gui_handlers[id(self.body_buffer)] = h4
        self.body_edit = GtkSource.View(buffer=self.body_buffer, expand = True)
        bodyscroll.add(self.body_edit)
        layout_left.attach(bodyscroll, 0, 4, 4, 1)

        # The closing:
        self.closing_buffer = GtkSource.Buffer(language=language)
        self.closing_buffer.set_text(default['closing'])
        h5 = self.closing_buffer.connect('changed', self.on_letter_changed)
        self.gui_handlers[id(self.closing_buffer)] = h5
        self.closing_edit = GtkSource.View(buffer=self.closing_buffer)
        layout_left.attach(self.closing_edit, 0, 5, 4, 1)

        # The PDF view:
        self.pdf_document_model = EvinceView.DocumentModel()
        self.pdf_view = EvinceView.View(expand = True)
        self.pdf_view.set_model(self.pdf_document_model)
        evscroll = Gtk.ScrolledWindow()
        evscroll.add(self.pdf_view)
        layout.add2(evscroll)

        # The progress bar:
        progress_layout = Gtk.Box()
        self.spinner = Gtk.Spinner()
        progress_layout.pack_start(self.spinner, False, False, 0)
        self.spinner_label = Gtk.Label("", halign=Gtk.Align.START)
        progress_layout.pack_start(self.spinner_label, True, True, 0)
        layout_left.attach(progress_layout, 0, 6, 2, 1)

        self.add(layout)

        self.show_all()

        # Get a hopefully DPI-aware height measure from the
        # drawn label:
        # TODO: This label is actually resized to the ComboBox size.
        # Use a label that is purely sized by the font size.
        font_height = 0.5 * label_sender.get_allocated_height()

        layout_left.set_row_spacing(max(round(0.2*font_height), 1))
        layout_left.set_column_spacing(max(round(0.2*font_height), 1))

        # Set a DPI-aware size request:
        layout.set_size_request(round(font_height * 80),
                                round(font_height * 40))
        layout_left.set_size_request(round(font_height * 35),
                                     round(font_height * 40))
        evscroll.set_size_request(round(font_height * 45),
                                  round(font_height * 40))


    def compute_contacts_hash(self):
        """
        Compute a hash that identifies the current contact information.
        """
        return hash((self.default_sender, tuple(self.addresses),
                     tuple(self.people)))


    def generate_contact_list_model(self):
        """
        Generates a GtkListStore model from the list of addresses.
        """
        model = Gtk.ListStore(str)
        for p in self.people:
            model.append((p.name,))
        return model


    def get_letter_content(self):
        """
        Compose the letter from the GUI element content.
        """
        sender = self.sender
        if sender is not None:
            sender = self.people[sender]
        destination = self.destination
        if destination is not None:
            destination = self.people[destination]

        # Content of the text editors:
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

        return sender, destination, subject, opening, body, closing


    def generate_letter(self):
        """
        Generates the letter from the current content.
        """
        self.sender = self.cb_sender.get_active()
        if self.sender == -1:
            self.sender = None
        self.destination = self.cb_destination.get_active()
        if self.destination == -1:
            self.destination = None
        # Early exit if one of the people is not set:
        if self.destination is None or self.sender is None:
            return

        # Get the content of the GUI elements:
        sender, destination, subject, opening, body, closing \
           = self.get_letter_content()

        # Start the compilation feedback:
        self.start_compiling()

        # Notify the task manager:
        self.emit("letter_changed",
                  Letter(sender, destination, subject, opening, body, closing),
                  Design(),
                  "scrletter")

    def log_error(self, error):
        """
        This method logs the error.
        """
        # Easy version right now:
        print("Error:",str(error))

    def on_letter_changed(self, *args):
        """
        General purpose slot called when the letter is changed.
        """
        self.generate_letter()

    def start_compiling(self):
        """
        Visual feedback that a LaTeX job is running.
        """
        self.spinner.start()
        self.spinner_label.set_text(" compiling...")
        self.save_pdf_button.set_sensitive(False)

    def finish_compiling(self):
        """
        Visual feedback that no LaTeX job is running any more.
        """
        self.spinner.stop()
        self.spinner_label.set_text("")
        self.save_pdf_button.set_sensitive(True)

    def on_receive_result(self, result: TaskResult):
        """
        Load the document generated by a LaTeX task.
        """
        # Stop the spinner:
        self.finish_compiling()

        # Load or reload the document:
        if self.document_path != result.document_path:
            self.document = EvinceDocument.Document.factory_get_document(
                result.document_path
            )
            self.pdf_document_model.set_document(self.document)
            self.document_path = result.document_path
        else:
            self.document.load(self.document_path)
            self.pdf_view.reload()

    def check_save_contacts_button(self):
        """
        Checks whether the 'Save Contacts' button should be updated.
        """
        contacts_hash = self.compute_contacts_hash()
        if self.contacts_hash != contacts_hash:
            self.save_contacts_button.set_sensitive(True)


    def show_address_dialog(self, *args):
        """
        Shows a dialog to edit the address book.
        """
        dialog = ContactsDialog(self)
        dialog.set_data(self.addresses, self.people)
        dialog.connect("person_changed", self.on_person_change)
        dialog.run()
        dialog.destroy()


    def on_person_change(self, dialog, p_id: int):
        """
        This slot is called when a person has changed from the address
        dialog.
        """
        # Update the name model:
        if p_id == self.name_model.iter_n_children():
            # New row.
            self.name_model.append((self.people[p_id].name,))
        else:
            # Existing row:
            it = self.name_model.get_iter(p_id)
            self.name_model.set(it, 0, self.people[p_id].name)

        # Check if we need to enable the contacts save button:
        self.check_save_contacts_button()

        # Check if the person is part of this letter and, if so,
        # recompile:
        if self.sender == p_id or self.destination == p_id:
            self.generate_letter()


    def select_save_path(self, which: str, file_pattern_name: str,
                         file_pattern_glob: str) -> Optional[Path]:
        """
        This method will run a dialog to select the save path, and
        return it on success.
        """
        save_letter_dialog = Gtk.FileChooserDialog(
            parent = self,
            title = "Save " + which + " as",
            action = Gtk.FileChooserAction.SAVE
        )
        save_letter_dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE,
            Gtk.ResponseType.OK,
        )
        file_filter = Gtk.FileFilter()
        file_filter.set_name(file_pattern_name)
        file_filter.add_pattern(file_pattern_glob)
        save_letter_dialog.add_filter(file_filter)
        status = save_letter_dialog.run()
        path = None
        if status == Gtk.ResponseType.OK:
            path = Path(save_letter_dialog.get_filename())
            if path.is_dir():
                path = None

        # If path exists, ask for overwrite confirmation:
        if path is not None and path.exists():
            confirm_dialog = Gtk.MessageDialog(
                transient_for=save_letter_dialog,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text="File exists",
            )
            confirm_dialog.format_secondary_text(
                "Proceed with overwriting the existing file?"
            )
            response = confirm_dialog.run()

            if response == Gtk.ResponseType.CANCEL:
                # Do not overwrite!
                path = None
            confirm_dialog.destroy()

        save_letter_dialog.destroy()
        return path


    def on_save_letter_clicked(self, *args):
        """
        This slot is called when the letter save button is clicked.
        """
        # Make sure that a letter has been selected:
        if self.letter_save_path is None:
            self.letter_save_path \
               = self.select_save_path("letter", "Hurtigbrief files",
                                       "*.hbrief")

        # If that failed, do not save.
        if self.letter_save_path is None:
            return

        # Save the letter:
        sender, destination, subject, opening, body, closing \
           = self.get_letter_content()

        # JSON serialization:
        if sender is not None:
            sender = sender.to_json()
        if destination is not None:
            destination = destination.to_json()
        try:
            with open(self.letter_save_path, 'w') as f:
                json.dump((sender, destination, subject, opening, body,
                           closing), f)
        except e:
            self.log_error(e)


    def select_letter_load_path(self) -> Optional[Path]:
        """
        This method will run a dialog to select the load path, and
        return it on success.
        """
        load_letter_dialog = Gtk.FileChooserDialog(
            parent = self,
            title = "Load letter",
            action = Gtk.FileChooserAction.SAVE
        )
        load_letter_dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )
        file_filter = Gtk.FileFilter()
        file_filter.set_name("Hurtigbrief files")
        file_filter.add_pattern("*.hbrief")
        load_letter_dialog.add_filter(file_filter)
        status = load_letter_dialog.run()
        path = None
        if status == Gtk.ResponseType.OK:
            path = Path(load_letter_dialog.get_filename())
            if not path.is_file():
                path = None

        load_letter_dialog.destroy()
        return path


    def on_load_letter_clicked(self, *args):
        """
        This slot is called when the letter load button is clicked.
        """
        # Select the letter to load:
        letter_load_path = self.select_letter_load_path()

        # If that failed, do not save.
        if letter_load_path is None:
            return

        # load the letter:
        try:
            with open(letter_load_path, 'r') as f:
                sender, destination, subject, opening, body, closing \
                   = json.load(f)
        except e:
            self.log_error(e)
            return

        # A map that links addresses to the location in the address list:
        a2i = {a : i for i,a in enumerate(self.addresses)}

        # Reset the sender and destination so that we can safely call
        # on_person_change without triggering a regeneration on each call:
        self.sender = None
        self.destination = None

        # Obtain the addresses:
        if sender is not None:
            sender_address = address_from_json(sender["address"])
            if sender_address in a2i:
                sai = a2i[sender_address]
            else:
                sai = len(self.addresses)
                self.addresses.append(sender_address)
            sender["address"] = sai

            # Generate the Person:
            sender = Person.from_json(sender, self.addresses)
            if sender in self.p2i:
                si = self.p2i[sender]
            else:
                si = len(self.people)
                self.people.append(sender)

            # Now update the GUI:
            self.on_person_change(self, si)


        if destination is not None:
            destination_address = address_from_json(destination["address"])
            if destination_address in a2i:
                dai = a2i[destination_address]
            else:
                dai = len(self.addresses)
                self.addresses.append(destination_address)
            destination["address"] = dai

            # Generate the Person:
            destination = Person.from_json(destination, self.addresses)
            if destination in self.p2i:
                di = self.p2i[destination]
                self.destination = self.people[di]
            else:
                di = len(self.people)
                self.people.append(destination)

            self.on_person_change(self, di)

        # Select sender and destination ids:
        self.sender = si
        self.destination = di
        with self.cb_sender.handler_block(
            self.gui_handlers[id(self.cb_sender)]
        ):
            self.cb_sender.set_active(si)
        with self.cb_destination.handler_block(
            self.gui_handlers[id(self.cb_destination)]
        ):
            self.cb_destination.set_active(di)

        # Set the texts:
        with self.subject_buffer.handler_block(
                self.gui_handlers[id(self.subject_buffer)]
        ):
            self.subject_buffer.set_text(subject)
        with self.opening_buffer.handler_block(
                self.gui_handlers[id(self.subject_buffer)]
        ):
            self.opening_buffer.set_text(opening)
        with self.body_buffer.handler_block(
                self.gui_handlers[id(self.body_buffer)]
        ):
            self.body_buffer.set_text(body)
        with self.body_buffer.handler_block(
                self.bui_handlers[id(self.closing_buffer)]
        ):
            self.closing_buffer.set_text(closing)

        # Generate the letter:
        self.generate_letter()


    def on_save_pdf_clicked(self, *args):
        """
        Saves the PDF, potentially opening a save path dialog before.
        """
        # Make sure that a letter has been selected:
        if self.pdf_save_path is None:
            self.pdf_save_path = self.select_save_path("PDF", "PDF files",
                                                       "*.pdf")

        # If that failed, do not save.
        if self.pdf_save_path is None:
            return

        # Save the PDF.
        # The path in `self.document_path` is a URI starting with
        # 'file://'. Split this prefix here:
        doc = self.document_path[7:]
        copyfile(doc, self.pdf_save_path)


    def on_save_contacts_clicked(self, *args):
        """
        Saves the contact list.
        """
        save_contacts(self.default_sender, self.addresses, self.people)

        # Disable the button:
        self.contacts_hash = self.compute_contacts_hash()
        self.save_contacts_button.set_sensitive(False)
