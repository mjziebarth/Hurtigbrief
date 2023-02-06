# A template letter.
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

from hurtigbrief.abstraction import Letter, Person, GermanAddress, Design
from hurtigbrief.latex.mklatex import do_latex
from hurtigbrief.latex.workspace import Workspace
from hurtigbrief.latex.preamblecache import PreambleCache
design = Design()
workspace = Workspace()
preamble_cache = PreambleCache(workspace)

# Compose a bogus letter:
sender_address = GermanAddress("Panorama­straße", "1A", "10178", "Berlin")
sender = Person("Max Mustermann", sender_address, "mm@hisowndomain.cool")
receiver_address = GermanAddress("Alte Post", "4", "18055", "Rostock")
receiver = Person("Maxi Muster", receiver_address, "mm@blablub.cool")
letter = Letter(
    sender, receiver, "Über die Anhörung",
    "Hallo Maxi",
    "was war denn da letztens los? Überall habe ich nur Schlimmes gehört! "
    "Man könnte meinen, das wäre vollkommen in die Hose gegangen. Hast du "
    "denn wenigstens den Quark mitbringen können? Den leckeren sahnigen "
    "Himbeerquark im 500\,g Becher. Darauf freue ich mich schon seit letztem "
    "Donnerstag!",
    "Liebe Grüße"
)

do_latex(letter, design, "scrletter", workspace, preamble_cache)
