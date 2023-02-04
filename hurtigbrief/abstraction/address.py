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

    def compose(self, international: bool = False) -> List[str]:
        country = []
        if international:
            country.append("Germany")
        if self.plz_only:
            return [str(self.postalcode) + " " + self.city] + country
        return [GermanAddress.format_street(self.street) + " " + self.number,
                str(self.postalcode) + " " + self.city] + country

    @staticmethod
    def format_street(strasse: str) -> str:
        """
        This function formats streets with shortened syntax
        (e.g. Brandenburger Straße -> Brandenburger Str.)
        """
        strasse = strasse.strip()
        if strasse[-7:] == "strasse" or strasse[-6:] == "straße" \
           or strasse[-7:] == "Strasse" or strasse[-6:] == "Straße":
            return strasse[:-4] + "."

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
                number = ""
        else:
            plz_only = True
            number = None
            street = None

        return GermanAddress(street, number, postalcode, city)

    raise NotImplementedError("Only 'GermanAddress' implemented so far.")
