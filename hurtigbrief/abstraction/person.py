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
from typing import Optional, List


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
        # Ensure that None and "" map to None:
        if email is not None:
            email = str(email)
            if len(email) == 0:
                email = None
        if phone is not None:
            phone = str(phone)
            if len(phone) == 0:
                phone = None
        self.email = email
        self.phone = phone


    def __hash__(self):
        return hash((self.name, self.address, self.email, self.phone))


    def compose_address(self) -> str:
        """
        Compose an address.
        """
        return "\\\\".join([self.name] + self.address.compose())


    @staticmethod
    def from_json(json: dict, address_list: List[Address]) -> "Person":
        """
        Load this person from a saved JSON.
        """
        aid = int(json["address"])
        if aid < 0 or aid > len(address_list):
            raise RuntimeError("JSON for a person is corrupted: found "
                               "address id " + str(aid) + " which is out of "
                               "bounds for an address list of length "
                               + str(len(address_list)) + ".")
        return Person(json["name"], address_list[aid], json["email"],
                      json["phone"])


    def to_json(self) -> dict:
        """
        JSON-serialize this Person.
        """
        return {
            "name" : self.name,
            "address" : self.address.to_json(),
            "email" : self.email,
            "phone" : self.phone
        }
