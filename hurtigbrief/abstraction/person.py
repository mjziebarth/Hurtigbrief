# A person.
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

from .address import Address
from typing import Optional


class Person:
    """
    A juridicial person.
    """
    # Attributes:
    name: str
    address: Address
    email: Optional[str] = None
    phone: Optional[str] = None


    def __init__(self, name: str, address: Address,
                 email: Optional[str] = None,
                 phone: Optional[str] = None):
        if not isinstance(address, Address):
            raise TypeError("`address` has to be an `Address` instance.")
        self.name = str(name)
        self.address = address
        self.email = str(email) if email is not None else None
        self.phone = str(phone) if phone is not None else None


    def compose_address(self) -> str:
        """
        Compose an address.
        """
        return "\\\\".join([self.name] + self.address.compose())
