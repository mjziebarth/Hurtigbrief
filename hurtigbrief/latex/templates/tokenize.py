# Token replacement in the LaTeX templates.
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

class Tokenizer:
    """
    Reads tokens from a template and prepares a data structure that allows
    for fast token replacement.
    """
    def __init__(self, tex: str, tokens: list):
        # Split the tex file on double percent signs:
        split = tex.split("%%")

        # Now each of the elements of split from index 1 and onward
        # contains a string that should start with a token minus the %%.
        substitute = [] if len(split[0]) < 1 else [(None, split[0])]
        for s in split[1:]:
            found = False
            for tok in tokens:
                if s.startswith(tok[2:]):
                    substitute.append((tok, s[len(tok)-2:]))
                    found = True
                    break
            if not found:
                raise RuntimeError("Could not substitute token starting with "
                                   + s[:10])
        self.substitute_list = substitute

    def substitute(self, tokens: dict) -> str:
        """
        Substitutes a token dictionary.
        """
        substituted = []
        for tok,text in self.substitute_list:
            if tok is not None:
                substituted.append(tokens[tok])
            substituted.append(text)
        return "".join(substituted)


def substitute_tokens(tex: str, tokens: dict):
    """
    Scans tokens of the format "%%TOKEN" in the latex template.
    For simplicity, this algorithm splits the template at occurrences
    of '%%'.
    """
    # Split the tex file on double percent signs:
    split = tex.split("%%")

    # Now each of the elements of split from index 1 and onward
    # contains a string that should start with a token minus the %%.
    substituted = [] if len(split[0]) < 1 else [split[0]]
    for s in split[1:]:
        found = False
        for tok,sub in tokens.items():
            if s.startswith(tok[2:]):
                substituted.append(sub + s[len(tok)-2:])
                found = True
                break
        if not found:
            raise RuntimeError("Could not substitute token starting with "
                               + s[:10])

    return "".join(substituted)
