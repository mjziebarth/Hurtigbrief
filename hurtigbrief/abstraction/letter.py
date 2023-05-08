# Class that represents a letter.
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

from .person import Person
from typing import Optional

class Letter:
    """
    A letter.
    """
    sender: Person
    destination: Person
    subject: str
    opening: str
    body: str
    closing: str
    signature: Optional[str]

    def __init__(self, sender: Person, destination: Person,
                 subject: str, opening: str, body: str, closing: str,
                 signature: Optional[str]):
        assert isinstance(sender, Person)
        assert isinstance(destination, Person)
        self.sender = sender
        self.destination = destination
        self.subject = str(subject)
        self.opening = str(opening)
        self.body = str(body)
        self.closing = str(closing)
        self.signature = str(signature) if signature is not None else None
