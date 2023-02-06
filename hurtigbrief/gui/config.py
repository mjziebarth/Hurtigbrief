# Configurations
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

import json

# The default configuration:
default = {
    "closing" : "Mit freundlichen Grüßen",
    "opening" : "Moin moin",
    "default_sender" : 0,
    #
    # Addresses:
    #
    "addresses" : [
        {
            "country"    : "Germany",
            "street"     : "Panoramastraße",
            "number"     : "1A",
            "postalcode" : 10178,
            "city"       : "Berlin"
        },
        {
            "country"    : "Germany",
            "street"     : "Alte Post",
            "number"     : "4",
            "postalcode" : 18055,
            "city"       : "Rostock"
        }
    ],
    #
    # People:
    #
    'people'  : [
        {
            'name'    : 'Zure Laki',
            'address' : 0,
            'email'   : 'muster@keinegueltigeemail.de',
            'phone'   : '(0)30 23125837',
        },
        {
            'name'    : 'Max Muster',
            'address' : 1,
            'email'   : 'muster@keinegueltigeemail.de',
            'phone'   : '(0)40 66969092',
        },
    ]
}
