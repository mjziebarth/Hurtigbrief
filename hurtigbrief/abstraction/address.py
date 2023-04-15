# An address.
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

from typing import Optional, List

class Address:
    """
    An address.
    """
    street: str
    number: str
    postalcode: int
    city: str

    def __init__(self, street: str, number: Optional[str],
                 postalcode: int, city: str):
        self.street = str(street)
        self.number = str(number) if number is not None else None
        self.postalcode = int(postalcode)
        self.city = str(city)

    def __hash__(self):
        return hash((self.street, self.number, self.postalcode, self.city))

    def compose(self) -> List[str]:
        raise NotImplementedError("Address compose not implemented for address "
                                  "of type " + str(type(self)))

    def to_json(self) -> dict:
        return {
            "street" : self.street,
            "number" : self.number,
            "postalcode" : self.postalcode,
            "city"   : self.city
        }


class GermanAddress(Address):
    """
    An address in Germany.
    """
    plz_only: bool
    def __init__(self,
                 strasse: Optional[str] = None,
                 hausnummer: Optional[str] = None,
                 plz: int = 0,
                 stadt: str = ""):
        self.plz_only = strasse is None and hausnummer is None
        if strasse is not None:
            strasse = str(strasse)
        if hausnummer is not None:
            hausnummer = str(hausnummer)
        super().__init__(strasse, hausnummer, int(plz), str(stadt))

    def __hash__(self):
        return hash((self.street, self.number, self.postalcode, self.city,
                     self.plz_only))

    def compose(self, international: bool = False) -> List[str]:
        country = []
        if international:
            country.append("Germany")
        if self.plz_only:
            return [str(self.postalcode) + " " + self.city] + country
        strnum = GermanAddress.format_street(self.street)
        if self.number is not None:
            strnum += " " + self.number
        return [strnum, str(self.postalcode) + " " + self.city] + country

    @staticmethod
    def parse_address(addr: str) -> "GermanAddress":
        """
        Parse this German address from a string.

        The address is expected in the following format:
           STREET NAME XY, PLZ CITY NAME
        where "STREET NAME" is the (possibly multi-worded) street
        name, "XY" the one-word house number, "PLZ" the one-word
        postal code, and "CITY NAME" the (possibly multi-worded)
        city name.

        This algorithm should cover most use cases but some degree of
        `falsehoods <https://www.mjt.me.uk/posts/falsehoods-programmers-believe-about-addresses/>`_
        is possible.
        """
        # Some string homogenization:
        addr = addr.strip()

        # Empty (invalid) default address:
        if len(addr) == 0:
            return GermanAddress()

        # Split the address by the comma:
        strnum, zipcity = addr.split(",")

        # Get street and number from the first half:
        strnum_split = strnum.split()
        if len(strnum_split) > 1:
            if any(c.isdigit() for c in strnum_split[-1]):
                number = strnum_split[-1]
                street = " ".join(strnum_split[:-1])
            else:
                number = None
                street = " ".join(strnum_split)
        elif len(strnum) > 0:
            street = strnum
            number = None
        else:
            street = None
            number = None

        # Get postal code and city from the second half:
        zipcity_split = zipcity.split()
        if len(zipcity_split) <= 1:
            raise ValueError("Postal code and city need to be given.")
        plz = int(zipcity_split[0])
        city = " ".join(zipcity_split[1:])

        return GermanAddress(street, number, plz, city)


    @staticmethod
    def format_street(strasse: str) -> str:
        """
        This function formats streets with shortened syntax
        (e.g. Brandenburger Straße -> Brandenburger Str.)
        """
        strasse = strasse.strip()
        if strasse[-7:] == "strasse" or strasse[-7:] == "Strasse":
            return strasse[:-4] + "."
        elif strasse[-6:] == "straße" or strasse[-6:] == "Straße":
            return strasse[:-3] + "."

        return strasse

    def to_json(self) -> dict:
        """
        Return a JSON element for saving this address.
        """
        json = super().to_json()
        if self.plz_only:
            del json["street"]
            del json["number"]
        return json


def address_from_json(json: dict) -> Address:
    """
    Generate an address from a JSON entry of the GUI.
    """
    country = json["country"]
    city = json["city"]
    postalcode = json["postalcode"]
    if country == "Germany":
        if "street" in json:
            plz_only = False
            street = json["street"]
            if "number" in json:
                number = json["number"]
            else:
                number = None
        else:
            plz_only = True
            number = None
            street = None

        return GermanAddress(street, number, postalcode, city)

    raise NotImplementedError("Only 'GermanAddress' implemented so far.")
