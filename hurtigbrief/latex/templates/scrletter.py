# LaTeX template substitution based on the scrletter LaTeX documenttype.
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

from pathlib import Path
from typing import Tuple
from ...abstraction import Letter, Design
from .tokenize import Tokenizer

def load_scrletter_template() -> Tuple[str,str]:
    """
    Loads the scrletter template.
    """
    from importlib.resources import files
    tex = files('hurtigbrief.latex.templates.data').joinpath('scrletter.tex')\
            .read_text()
    preamble = files('hurtigbrief.latex.templates.data')\
                 .joinpath('scrletter-preamble.tex').read_text()
    return tex, preamble


ALL_TOKENS = ["%%FROMEMAILFLAG", "%%FROMEMAIL", "%%FROMPHONEFLAG",
              "%%FROMPHONE", "%%FROMNAME", "%%FROMZIPCODE", "%%FROMADDRESS",
              "%%TOADDRESS", "%%SUBJECT", "%%OPENING", "%%CONTENT",
              "%%CLOSING", "%%FONT"]

_scrletter_tex, _scrletter_preamble_tex = load_scrletter_template()
_scrletter_tokenizer = Tokenizer(_scrletter_tex, ALL_TOKENS)
_scrletter_preamble_tokenizer = Tokenizer(_scrletter_preamble_tex, ALL_TOKENS)

def create_scr_letter(letter: Letter, design: Design) -> Tuple[str,str]:
    """
    Creates a KOMA ScrLetter.
    """
    # Load the template:
    tex = _scrletter_tex

    # Create the token dictionary:
    token_map = {}

    # E-Mail address:
    if letter.sender.email is None:
        token_map["%%FROMEMAILFLAG"] = "false"
        token_map["%%FROMEMAIL"] = ""
    else:
        token_map["%%FROMEMAILFLAG"] = "true"
        token_map["%%FROMEMAIL"] = letter.sender.email

    # Phone number:
    if letter.sender.phone is None:
        token_map["%%FROMPHONEFLAG"] = "false"
        token_map["%%FROMPHONE"] = ""
    else:
        token_map["%%FROMPHONEFLAG"] = "true"
        token_map["%%FROMPHONE"] = letter.sender.phone

    token_map["%%FROMNAME"] = letter.sender.name
    token_map["%%FROMZIPCODE"] = str(letter.sender.address.postalcode)
    token_map["%%FROMADDRESS"] = "\n".join(letter.sender.address.compose())
    token_map["%%TOADDRESS"] = letter.destination.compose_address()

    # Letter content:
    token_map["%%SUBJECT"] = letter.subject
    if letter.opening.strip()[-1] == ',':
        token_map["%%OPENING"] = letter.opening
    else:
        token_map["%%OPENING"] = letter.opening + ","
    token_map["%%CONTENT"] = letter.body
    token_map["%%CLOSING"] = letter.closing


    # Letter style:
    token_map["%%FONT"] = design.font

    return (_scrletter_preamble_tokenizer.substitute(token_map),
            _scrletter_tokenizer.substitute(token_map))

